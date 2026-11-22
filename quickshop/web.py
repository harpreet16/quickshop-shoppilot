"""Session-owned browser bridge. Worker threads never call Streamlit APIs."""

import json
from queue import Empty, Queue
from threading import Lock, Thread
from urllib.parse import urlsplit

from strands import tool

from quickshop.agent.orchestrator import build_agent
from quickshop.agent.prompts import build_instructions
from quickshop.tools import DEFAULT_TOOLS
from quickshop.tools.scoring import score_product

PILOT_QUERY = "black straight-leg jeans, size 32 waist, under $80"


def result_data(call):
    """Decode Strands tool results, not model-authored Markdown."""
    if call.get("blocked") or call.get("status") != "success":
        return None
    for block in call.get("result", {}).get("content", []):
        if "json" in block:
            return block["json"]
        try:
            return json.loads(block.get("text", ""))
        except (ValueError, TypeError):
            continue
    return None


def results_to_cards(calls):
    listings, scores, merchants = {}, {}, {}
    selection, reasons = set(), {}
    for call in calls:
        data = result_data(call)
        if call["tool"] == "search_listings" and isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get("url"):
                    listings[item["url"]] = item
        elif isinstance(data, dict):
            if call["tool"] == "show_results":
                selection = set(data.get("recommendations", []))
                reasons = data.get("not_recommended", {})
            if call["tool"] == "score_product" and data.get("url"):
                scores[data["url"]] = data
            elif call["tool"] == "check_merchant" and data.get("merchant"):
                merchants[data["merchant"]] = data
    recommended, rejected = [], []
    for url, item in listings.items():
        signals = merchants.get(item.get("merchant"))
        merchant_score = None
        if signals:
            merchant_score = score_product(
                url=url,
                price=item.get("price"),
                **{
                    key: signals.get(key)
                    for key in (
                        "known_brand",
                        "domain_age_years",
                        "third_party_reviews",
                        "return_policy",
                    )
                },
            )
        score = scores.get(url)
        # A rejected seller stays rejected even if later model-supplied scoring inputs disagree.
        if (
            merchant_score
            and not merchant_score["eligible"]
            and (not score or score.get("eligible"))
        ):
            score = merchant_score
        if url in reasons:
            score = {
                **(score or {}),
                "eligible": False,
                "available": True,
                "evidence": [reasons[url], *(score or {}).get("evidence", [])],
            }
        elif url not in selection and (not score or score.get("eligible")):
            continue
        if not score or not score.get("available"):
            continue
        try:
            safe_link = urlsplit(url).scheme in ("http", "https") and bool(urlsplit(url).netloc)
        except ValueError:
            safe_link = False
        card = {
            "title": item.get("title", "Unknown product"),
            "price": item.get("price"),
            "merchant": item.get("merchant", "Unknown seller"),
            "url": url if safe_link else None,
            "scores": score,
            "evidence": score.get("evidence", []),
        }
        (recommended if score.get("eligible") is True else rejected).append(card)
    recommended.sort(key=lambda card: card["scores"].get("overall") or 0, reverse=True)
    return recommended, rejected


class WebSession:
    def __init__(self, frozen=False, factory=build_agent):
        self.frozen = frozen
        self.events = Queue()
        self.answers = Queue()
        self.lock = Lock()
        self.question_lock = Lock()
        self.busy = False
        self.waiting = False
        self.agent = None
        self.thread = None
        self.factory = factory

    def ask(self, question):
        with self.lock:
            self.waiting = True
        self.events.put(("question", question))
        try:
            # Bound abandoned browser sessions rather than leave a waiting thread forever.
            return self.answers.get(timeout=300) or "No answer given. Continue without it."
        except Empty:
            return "The shopper did not reply within five minutes. Stop and ask them to return."
        finally:
            with self.lock:
                self.waiting = False

    def answer(self, text):
        with self.lock:
            if not self.waiting:
                raise RuntimeError("No clarification is awaiting an answer")
            self.waiting = False
            self.answers.put(text)

    def start(self, request):
        with self.lock:
            if self.busy:
                raise RuntimeError("A shopping request is already running")
            self.busy = True
        self.thread = Thread(target=self._run, args=(request,), daemon=True)
        self.thread.start()

    def _run(self, request):
        try:
            if self.agent is None:

                @tool
                def ask_user(question: str) -> str:
                    """Ask the shopper one clarification question in browser chat."""
                    with self.question_lock:
                        return self.ask(question)

                if self.frozen:
                    from quickshop.frozen import frozen_tools

                    tools = frozen_tools(ask_user)
                else:
                    tools = [ask_user if t.tool_name == "ask_user" else t for t in DEFAULT_TOOLS]

                @tool
                def show_results(
                    recommendations: list[str], not_recommended: dict[str, str]
                ) -> dict:
                    """Publish final product cards after scoring. Use listing URLs, not invented products.
                    recommendations contains chosen URLs only. not_recommended maps rejected URLs to reasons.
                    """
                    return {"recommendations": recommendations, "not_recommended": not_recommended}

                instructions = build_instructions(5) + (
                    "\nYou are in a browser. ask_user waits for a browser reply, not terminal input. "
                    "After scoring, ALWAYS call show_results to publish your final chosen products and "
                    "rejection reasons. Include checked but rejected sellers. Do not recommend every scored "
                    "product: choose only those matching the shopper's request and evidence requirements."
                )
                self.agent = self.factory(tools=[*tools, show_results], instructions=instructions)
                self.agent.trace.on_call = lambda call: self.events.put(("call", call))
                self.agent.trace.on_start = lambda call: self.events.put(("tool_start", call))
            self.events.put(("message", str(self.agent(request))))
        except Exception:  # noqa: BLE001 — redact provider failures at the browser boundary.
            # Provider exception text can include request URLs or credentials. Keep it server-side.
            self.events.put(
                ("error", "Request failed. Check server configuration, API access and credits.")
            )
        finally:
            self.busy = False
            self.events.put(("done", None))
