"""Browser bridge and UI checks; no model, search, or scraper requests."""

import json
from types import SimpleNamespace

import pytest

from quickshop.agent.hooks import TraceLogger
from quickshop.frozen import PRODUCTS, frozen_tools
from quickshop.web import PILOT_QUERY, WebSession, result_data, results_to_cards


def call(name, data, **extra):
    return {
        "tool": name,
        "input": {},
        "status": "success",
        "blocked": False,
        "result": {"content": [{"text": json.dumps(data)}]},
        **extra,
    }


def demo_calls():
    tools = {t.tool_name: t for t in frozen_tools(None) if t is not None}
    calls = [call("search_listings", tools["search_listings"](PILOT_QUERY))]
    for item in PRODUCTS:
        signals = tools["check_merchant"](item["merchant"])
        calls.append(call("check_merchant", signals))
        evidence = tools["fetch_product_evidence"](item["url"])
        scores = tools["score_product"](
            url=item["url"],
            price=item["price"],
            natural_fiber_pct=evidence["natural_fiber_pct"],
            **{
                key: signals[key]
                for key in (
                    "known_brand",
                    "domain_age_years",
                    "third_party_reviews",
                    "return_policy",
                )
            },
        )
        calls.append(call("score_product", scores))
    calls.append(
        call(
            "show_results",
            {
                "recommendations": [PRODUCTS[0]["url"]],
                "not_recommended": {
                    PRODUCTS[1]["url"]: "Fabric composition is unverified",
                    PRODUCTS[2]["url"]: "Unknown seller; no return-policy evidence",
                },
            },
        )
    )
    return calls


def test_cards_rank_and_reject_ebay_without_parsing_model_prose():
    recommended, rejected = results_to_cards(demo_calls())
    assert [card["merchant"] for card in recommended] == ["Kohl's"]
    assert [card["merchant"] for card in rejected] == ["Gap", "eBay - authenticbargainsllc"]
    assert rejected[1]["scores"]["eligible"] is False
    assert "Unknown seller" in " ".join(rejected[1]["evidence"])


def test_missing_blocked_and_malformed_results_are_not_cards():
    assert result_data(call("score_product", {}, blocked=True)) is None
    assert result_data({"status": "success", "result": {"content": [{"text": "not JSON"}]}}) is None
    assert results_to_cards([call("search_listings", PRODUCTS)]) == ([], [])


def test_rejected_merchant_cannot_be_promoted_by_model_score_inputs():
    calls = demo_calls()
    calls.append(
        call(
            "score_product",
            {"url": PRODUCTS[-1]["url"], "eligible": True, "available": True, "overall": 5},
        )
    )
    calls.append(
        call(
            "show_results",
            {
                "recommendations": [PRODUCTS[0]["url"], PRODUCTS[2]["url"]],
                "not_recommended": {PRODUCTS[1]["url"]: "Unverified fabric"},
            },
        )
    )
    assert len(results_to_cards(calls)[1]) == 2


def test_cards_reject_executable_links():
    calls = [
        call("search_listings", [{**PRODUCTS[0], "url": "javascript:alert(1)"}]),
        call(
            "score_product",
            {"url": "javascript:alert(1)", "eligible": True, "available": True, "overall": 4},
        ),
    ]
    calls.append(call("show_results", {"recommendations": ["javascript:alert(1)"]}))
    assert results_to_cards(calls)[0][0]["url"] is None


def test_trace_observer_keeps_existing_trace_shape():
    trace, observed = TraceLogger(), []
    trace.on_call = observed.append
    event = SimpleNamespace(
        tool_use={"name": "search_listings", "input": {"query": "jeans"}},
        result={"status": "success", "content": [{"json": PRODUCTS}]},
        cancel_message=None,
    )
    trace.log(event)
    assert observed == [{**trace.calls[0], "result": event.result}]
    assert result_data(observed[0]) == PRODUCTS


def test_web_clarification_resumes_same_agent_and_followups():
    agents = []

    def factory(tools, **kwargs):
        class FakeAgent:
            def __init__(self):
                self.trace = TraceLogger()
                self.budget = SimpleNamespace(credits=5, used=0)
                self.requests = []

            def __call__(self, request):
                self.requests.append(request)
                if len(self.requests) == 1:
                    ask = next(t for t in tools if t.tool_name == "ask_user")
                    return "Size: " + ask(question="What size?")
                return "Follow-up received"

        agent = FakeAgent()
        agents.append(agent)
        return agent

    session = WebSession(frozen=True, factory=factory)
    session.start(PILOT_QUERY)
    assert session.events.get(timeout=5) == ("question", "What size?")
    with pytest.raises(RuntimeError, match="already running"):
        session.start("another request")
    session.answer("32")
    session.thread.join(timeout=5)
    assert not session.thread.is_alive()
    assert session.events.get_nowait() == ("message", "Size: 32")
    assert session.events.get_nowait() == ("done", None)
    session.start("Only cotton")
    session.thread.join(timeout=5)
    assert len(agents) == 1
    assert agents[0].requests == [PILOT_QUERY, "Only cotton"]
    assert not WebSession().waiting


def test_worker_errors_are_safe_and_clear_busy_state():
    def broken(**kwargs):
        raise RuntimeError("secret-key-do-not-display")

    session = WebSession(factory=broken)
    session.start("jeans")
    session.thread.join(timeout=5)
    events = list(session.events.queue)
    assert events[0][0] == "error"
    assert "secret-key" not in str(events)
    assert events[-1] == ("done", None)
    assert not session.busy


def test_frozen_tools_never_use_live_search_or_scraper(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Network requested")

    monkeypatch.setattr("httpx.Client.get", forbidden)
    monkeypatch.setattr(
        "quickshop.evidence.firecrawl_client.FirecrawlClient.scrape_product", forbidden
    )
    assert demo_calls()


def test_streamlit_initial_page_and_frozen_switch():
    streamlit = pytest.importorskip("streamlit.testing.v1")
    app = streamlit.AppTest.from_file("../app.py").run()
    assert not app.exception
    assert app.title[0].value == "QuickShop"
    assert app.metric[0].value == "5"
    app.toggle[0].set_value(True).run()
    assert not app.exception
    assert app.session_state.shop.frozen


def test_streamlit_renders_rejected_demo_card():
    streamlit = pytest.importorskip("streamlit.testing.v1")
    app = streamlit.AppTest.from_file("../app.py").run()
    app.session_state.calls = demo_calls()
    app.run()
    assert not app.exception
    assert "Not recommended" in [heading.value for heading in app.subheader]
    assert any("eBay - authenticbargainsllc" in text.value for text in app.text)
    assert any("Not recommended" in error.value for error in app.error)


def test_browser_pilot_question_reply_cards_and_followup():
    streamlit = pytest.importorskip("streamlit.testing.v1")

    def factory(tools, **kwargs):
        ask = next(t for t in tools if t.tool_name == "ask_user")

        class PilotAgent:
            trace = TraceLogger()
            budget = SimpleNamespace(credits=5, used=0)

            def __call__(self, request):
                answer = ask(question="What height?")
                for event in demo_calls():
                    self.trace.on_call(event)
                return f"Recommendations ready for {answer}"

        return PilotAgent()

    app = streamlit.AppTest.from_file("../app.py").run()
    session = WebSession(frozen=True, factory=factory)
    app.session_state.shop = session
    app.run()
    app.chat_input[0].set_value(PILOT_QUERY).run()
    app.run()
    assert session.waiting
    assert any(text.value == "What height?" for text in app.text)
    app.chat_input[0].set_value("170 cm").run()
    session.thread.join(timeout=5)
    app.run()
    assert not app.exception
    assert not session.busy
    assert any("eBay - authenticbargainsllc" in text.value for text in app.text)
    assert any("Recommendations ready for 170 cm" == text.value for text in app.text)
    assert all(not button.disabled for button in app.button)
