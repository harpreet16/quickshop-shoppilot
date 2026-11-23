"""
StreamingHook — pushes AfterToolCall events into an asyncio Queue from the agent thread,
so the SSE generator can forward them to the browser in real time.

It also remembers the listings the agent searched and the scores it computed, so the final
`done` event can carry structured `products` next to the agent's prose answer.
"""

import asyncio
import json
import logging

from strands.hooks import AfterToolCallEvent, HookProvider

logger = logging.getLogger(__name__)


def _result_json(result):
    """Parse the JSON a tool returned out of Strands' {"content": [{"text": ...}]} wrapper."""
    if not isinstance(result, dict):
        return None
    for block in result.get("content") or []:
        text = block.get("text") if isinstance(block, dict) else None
        if not text:
            continue
        try:
            return json.loads(text)
        except ValueError:
            continue
    return None


def _url_key(url) -> str:
    return str(url).strip()


class StreamingHook(HookProvider):
    def __init__(self, queue: asyncio.Queue, loop: asyncio.AbstractEventLoop):
        self._queue = queue
        self._loop = loop
        self.calls: list[dict] = []
        self._listings: dict[str, dict] = {}
        self._scored: dict[str, dict] = {}
        self._images: dict[str, str] = {}   # product page url -> image read from the page

    def register_hooks(self, registry, **kwargs):
        registry.add_callback(AfterToolCallEvent, self._on_tool_call)

    def _on_tool_call(self, event: AfterToolCallEvent):
        result = event.result
        status = (
            result.get("status", "success") if isinstance(result, dict) else "success"
        )
        call = {
            "tool": event.tool_use["name"],
            "status": status,
            "blocked": event.cancel_message is not None,
        }
        self.calls.append(call)
        try:
            self._collect(event)
        except Exception:
            logger.warning(
                "could not collect product data from %s", call["tool"], exc_info=True
            )
        # thread-safe push into the asyncio queue
        self._loop.call_soon_threadsafe(
            self._queue.put_nowait, {"event": "tool_call", "data": call}
        )

    def _collect(self, event: AfterToolCallEvent):
        if event.cancel_message is not None:
            return
        name = event.tool_use.get("name")
        data = _result_json(event.result)
        if name == "search_listings" and isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get("url") and item.get("title"):
                    self._listings[_url_key(item["url"])] = item
        elif name == "fetch_product_evidence" and isinstance(data, dict):
            image = data.get("image_url")
            if isinstance(image, str) and image.startswith(("http://", "https://")):
                for url in (data.get("url"), (event.tool_use.get("input") or {}).get("url")):
                    if url:
                        self._images[_url_key(url)] = image
        elif name == "score_product" and isinstance(data, dict):
            if data.get("url") and data.get("available", True):
                self._scored[_url_key(data["url"])] = {
                    "scores": data,
                    "inputs": dict(event.tool_use.get("input") or {}),
                }

    def products(self) -> list[dict]:
        """Every product the agent scored, eligible ones first, best overall score first."""
        items = []
        for key, entry in self._scored.items():
            scores = entry["scores"]
            inputs = entry["inputs"]
            listing = self._listings.get(key, {})
            items.append(
                {
                    "title": listing.get("title") or "Unnamed listing",
                    "merchant": listing.get("merchant") or "Unknown seller",
                    "price": listing.get("price", inputs.get("price")),
                    "rating": listing.get("rating"),
                    "reviews": listing.get("reviews"),
                    "url": scores["url"],
                    # the product page's own photo is best; the search thumbnail covers products with no page read
                    "image_url": self._images.get(key) or listing.get("thumbnail"),
                    "scores": {
                        k: scores.get(k)
                        for k in ("price", "quality", "legitimacy", "overall")
                    },
                    "eligible": bool(scores.get("eligible")),
                    "risk": scores.get("risk"),
                    "evidence": [str(line) for line in (scores.get("evidence") or [])],
                    "natural_fiber_pct": inputs.get("natural_fiber_pct"),
                    "composition": inputs.get("composition"),
                }
            )
        items.sort(key=lambda p: (not p["eligible"], -(p["scores"]["overall"] or 0)))
        return items
