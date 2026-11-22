"""Activity presentation and column placement, without live APIs."""

import json
from types import SimpleNamespace

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest

from quickshop.agent.hooks import TraceLogger
from quickshop.ui import event_summary_html, tool_presentation


def completed(tool, data, **extra):
    return {
        "tool": tool,
        "input": {"query": "black jeans"},
        "status": "success",
        "result": {"content": [{"json": data}]},
        **extra,
    }


@pytest.mark.parametrize(
    "event,tone,label",
    [
        (
            completed("score_product", {"eligible": False, "risk": "high"}),
            "error",
            "Not recommended",
        ),
        (completed("score_product", {"eligible": True, "risk": "low"}), "success", "low risk"),
        (completed("score_product", {"risk": "medium"}), "warning", "medium risk"),
        (completed("score_product", {"risk": "high"}), "error", "high risk"),
        (
            completed("fetch_product_evidence", {"status": "partial"}),
            "warning",
            "Incomplete evidence",
        ),
        (completed("fetch_product_evidence", {"status": "unavailable"}), "error", "Unavailable"),
        (
            completed("search_listings", [{"error": "Search timed out"}]),
            "error",
            "Search unavailable",
        ),
        (completed("fetch_product_evidence", {}, blocked=True), "warning", "Blocked"),
        ({"tool": "search_listings", "status": "running"}, "info", "Running"),
    ],
)
def test_tool_status_colors(event, tone, label):
    category, color, actual_tone, summary = tool_presentation(event)
    assert actual_tone == tone
    assert label in summary
    assert category and color


def test_trace_reports_start_and_completion_with_matching_id():
    trace, starts, finishes = TraceLogger(), [], []
    trace.on_start, trace.on_call = starts.append, finishes.append
    event = SimpleNamespace(
        tool_use={"toolUseId": "search-1", "name": "search_listings", "input": {}},
        result={"status": "success", "content": [{"text": "[]"}]},
        cancel_message=None,
    )
    trace.started(event)
    assert starts == [
        {"tool": "search_listings", "input": {}, "tool_id": "search-1", "status": "running"}
    ]
    assert not trace.calls
    trace.log(event)
    assert finishes[0]["tool_id"] == starts[0]["tool_id"]


def test_activity_updates_are_separate_from_central_chat():
    app = AppTest.from_file("../app.py").run()
    app.session_state.messages = [("user", "Find jeans"), ("assistant", "What size?")]
    app.session_state.shop.busy = True
    app.session_state.shop.events.put(
        (
            "tool_start",
            {
                "tool": "search_listings",
                "input": {"query": "black jeans"},
                "tool_id": "search-1",
                "status": "running",
            },
        )
    )
    app.run()
    chat, activity = app.get("column")
    assert [item.value for item in chat.text] == ["Find jeans", "What size?"]
    assert not chat.json
    assert any("Running" in item.value for item in activity.get("html"))
    assert "search-1" in app.session_state.running_tools

    result = completed("search_listings", [{"title": "Jeans"}], tool_id="search-1")
    app.session_state.shop.events.put(("call", result))
    app.run()
    chat, activity = app.get("column")
    assert not app.exception
    assert not app.session_state.running_tools
    assert [item.value for item in chat.text] == ["Find jeans", "What size?"]
    assert any("Completed" in item.value for item in activity.get("html"))
    assert json.loads(activity.json[-1].value) == [{"title": "Jeans"}]
    assert len(chat.chat_input) == 1
    assert not activity.chat_input


def test_summary_is_compact_and_escapes_seller_content():
    calls = [
        completed("check_merchant", {"merchant": f"Seller {i}", "known_brand": True})
        for i in range(12)
    ]
    calls.append(
        completed(
            "check_merchant",
            {"merchant": "Editorialist <script>alert(1)</script>", "known_brand": False},
        )
    )
    html = event_summary_html(calls)
    assert html.count("<tr class=") == 10
    assert "Seller 0</td>" not in html
    assert "Editorialist &lt;script&gt;" in html
    assert "Unrecognized seller" in html
    assert "<script>" not in html


def test_rejection_cards_are_red_in_activity_not_chat():
    app = AppTest.from_file("../app.py").run()
    url = "https://example.com/jeans"
    app.session_state.messages = [("assistant", "Here is your shopping summary.")]
    app.session_state.calls = [
        completed(
            "search_listings",
            [{"url": url, "title": "Demo jeans", "merchant": "eBay seller", "price": 35}],
        ),
        completed(
            "score_product",
            {
                "url": url,
                "available": True,
                "eligible": False,
                "risk": "high",
                "evidence": ["Seller could not be verified"],
            },
        ),
    ]
    app.run()
    chat, activity = app.get("column")
    assert not app.exception
    assert not chat.error
    assert [text.value for text in chat.text] == ["Here is your shopping summary."]
    assert any("Not recommended" in error.value for error in activity.error)
    assert any("eBay seller" in text.value for text in activity.text)
