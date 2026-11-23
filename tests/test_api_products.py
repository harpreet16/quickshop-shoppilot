import asyncio
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.api.hooks import StreamingHook  # noqa: E402


class _Loop:
    def call_soon_threadsafe(self, fn, *args):
        fn(*args)


def _hook():
    return StreamingHook(asyncio.Queue(), _Loop())


def _wrap(payload):
    return {"toolUseId": "t1", "status": "success", "content": [{"text": json.dumps(payload)}]}


def _event(name, payload, tool_input=None, cancel=None, raw=None):
    return SimpleNamespace(
        tool_use={"name": name, "input": tool_input or {}},
        result=raw if raw is not None else _wrap(payload),
        cancel_message=cancel,
    )


def _scores(url, overall, eligible=True, risk="low"):
    return {
        "url": url, "price": 4, "quality": 5, "legitimacy": 5 if eligible else 1,
        "overall": overall, "eligible": eligible, "risk": risk,
        "evidence": ["$25 → price score 4/5", "✓ Recognized brand/retailer"], "available": True,
    }


LISTINGS = [
    {"title": "Linen Shirt", "price": 24.99, "merchant": "Old Navy", "rating": 4.6, "reviews": 120, "url": "https://shop/a"},
    {"title": "Cotton Tee", "price": 12.0, "merchant": "Target", "rating": None, "reviews": None, "url": "https://shop/b"},
    {"title": "Mystery Top", "price": 9.0, "merchant": "Shady", "rating": None, "reviews": None, "url": "https://shop/c"},
]


def test_products_are_mapped_and_ordered_eligible_first_then_by_overall():
    hook = _hook()
    hook._on_tool_call(_event("search_listings", LISTINGS))
    hook._on_tool_call(_event("score_product", _scores("https://shop/c", 2.1, eligible=False, risk="high"), {"url": "https://shop/c", "price": 9.0}))
    hook._on_tool_call(_event("score_product", _scores("https://shop/b", 3.6), {"url": "https://shop/b", "price": 12.0}))
    hook._on_tool_call(_event(
        "score_product", _scores("https://shop/a", 4.4),
        {"url": "https://shop/a", "price": 24.99, "natural_fiber_pct": 100, "composition": {"linen": 100}},
    ))

    products = hook.products()

    assert [p["url"] for p in products] == ["https://shop/a", "https://shop/b", "https://shop/c"]
    best = products[0]
    assert best["title"] == "Linen Shirt"
    assert best["merchant"] == "Old Navy"
    assert best["price"] == 24.99
    assert best["rating"] == 4.6 and best["reviews"] == 120
    assert best["scores"] == {"price": 4, "quality": 5, "legitimacy": 5, "overall": 4.4}
    assert best["eligible"] is True and best["risk"] == "low"
    assert best["natural_fiber_pct"] == 100 and best["composition"] == {"linen": 100}
    assert best["evidence"][1].startswith("✓")
    assert products[2]["eligible"] is False and products[2]["risk"] == "high"


def test_score_without_a_matching_listing_falls_back_to_tool_input():
    hook = _hook()
    hook._on_tool_call(_event("score_product", _scores("https://other/z", 3.9), {"url": "https://other/z", "price": 18.5}))

    (product,) = hook.products()

    assert product["title"] == "Unnamed listing"
    assert product["merchant"] == "Unknown seller"
    assert product["price"] == 18.5


def test_blocked_and_malformed_tool_results_are_ignored_without_raising():
    hook = _hook()
    hook._on_tool_call(_event("score_product", _scores("https://shop/a", 4.0), cancel="budget used up"))
    hook._on_tool_call(_event("score_product", None, raw={"status": "success", "content": [{"text": "not json"}]}))
    hook._on_tool_call(_event("score_product", None, raw="plain string result"))
    hook._on_tool_call(_event("search_listings", [{"error": "No saved search", "available": False}]))

    assert hook.products() == []
    assert len(hook.calls) == 4


def test_unavailable_scores_are_not_listed():
    hook = _hook()
    hook._on_tool_call(_event("score_product", {**_scores("https://shop/a", 4.0), "available": False}))

    assert hook.products() == []


def test_sse_helper_emits_valid_json_for_python_values():
    pytest.importorskip("sse_starlette")
    from backend.api.routers.chat import _sse

    payload = {"tool": "check_merchant", "blocked": False, "note": "Levi's \"Black\"\nJeans", "none": None}
    event = _sse("tool_call", payload)

    assert event["event"] == "tool_call"
    assert json.loads(event["data"]) == payload


# ---- product photos

def test_image_prefers_the_page_photo_and_falls_back_to_the_search_thumbnail():
    hook = _hook()
    listings = [dict(LISTINGS[0], thumbnail="https://thumb/a.jpg"), dict(LISTINGS[1], thumbnail="https://thumb/b.jpg"), LISTINGS[2]]
    hook._on_tool_call(_event("search_listings", listings))
    hook._on_tool_call(_event(
        "fetch_product_evidence", {"url": "https://shop/a", "status": "ok", "image_url": "https://cdn/a-main.jpg"},
        {"url": "https://shop/a"},
    ))
    for url, overall in (("https://shop/a", 4.4), ("https://shop/b", 3.6), ("https://shop/c", 3.0)):
        hook._on_tool_call(_event("score_product", _scores(url, overall), {"url": url}))
    by_url = {p["url"]: p for p in hook.products()}
    assert by_url["https://shop/a"]["image_url"] == "https://cdn/a-main.jpg"   # page photo beats the thumbnail
    assert by_url["https://shop/b"]["image_url"] == "https://thumb/b.jpg"      # no page photo: thumbnail
    assert by_url["https://shop/c"]["image_url"] is None                       # nothing known: none, never invented


def test_failed_page_read_still_gets_the_thumbnail():
    hook = _hook()
    hook._on_tool_call(_event("search_listings", [dict(LISTINGS[0], thumbnail="https://thumb/a.jpg")]))
    hook._on_tool_call(_event("fetch_product_evidence", {"url": "https://shop/a", "status": "unavailable", "image_url": None}, {"url": "https://shop/a"}))
    hook._on_tool_call(_event("score_product", _scores("https://shop/a", 4.0), {"url": "https://shop/a"}))
    assert hook.products()[0]["image_url"] == "https://thumb/a.jpg"


def test_non_http_image_from_a_tool_is_ignored():
    hook = _hook()
    hook._on_tool_call(_event("search_listings", LISTINGS))
    hook._on_tool_call(_event("fetch_product_evidence", {"url": "https://shop/a", "image_url": "data:image/png;base64,AA"}, {"url": "https://shop/a"}))
    hook._on_tool_call(_event("score_product", _scores("https://shop/a", 4.0), {"url": "https://shop/a"}))
    assert hook.products()[0]["image_url"] is None
