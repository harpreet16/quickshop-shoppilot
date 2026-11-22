# Tests for eval/metrics.py and eval/recorder.py. Offline: they use the saved pilot outputs.
import json
from pathlib import Path
from types import SimpleNamespace

from eval.metrics import compute, picks_b0, picks_b1, picks_b2, picks_quickshop, score_run, to_markdown
from eval.recorder import ToolRecorder, read_tool_output

OUTPUTS = Path(__file__).parent.parent / "outputs"


def _text(name):
    return (OUTPUTS / name).read_text()


# A QuickShop run shaped like our pilot: Kohl's recommended, eBay seller blocked, Gap unverified.
KOHLS = "https://www.kohls.com/product/levis-classic-straight"
EBAY = "https://www.ebay.com/itm/levis-123"
GAP = "https://www.gapfactory.com/browse/456"
QUICKSHOP_RESULT = {
    "success": True,
    "elapsed_seconds": 95.2,
    "tool_calls": 27,
    "firecrawl_credits": 25,
    "output": (
        "Recommended:\n| Levi's Classic Straight Jeans | $48.65 | Kohl's | 4/4/4 | LOW |\n\n"
        "Not recommended:\n| eBay Levi's | $34.99 | authenticbargainsllc | legitimacy too low |\n"
        "| Gap Factory | $29.99 | Gap Factory | garbled page |\n"
    ),
    "tool_log": [
        {"tool": "fetch_product_evidence", "input": {"url": KOHLS},
         "output": {"url": KOHLS, "status": "ok", "natural_fiber_pct": 79.0}},
        {"tool": "fetch_product_evidence", "input": {"url": GAP},
         "output": {"url": GAP, "status": "partial", "natural_fiber_pct": None}},
        {"tool": "score_product", "input": {"url": KOHLS, "price": 48.65},
         "output": {"url": KOHLS, "legitimacy": 4, "eligible": True, "overall": 4.0}},
        {"tool": "score_product", "input": {"url": EBAY, "price": 34.99},
         "output": {"url": EBAY, "legitimacy": 2, "eligible": False, "overall": 3.1}},
        {"tool": "score_product", "input": {"url": GAP, "price": 29.99},
         "output": {"url": GAP, "legitimacy": 4, "eligible": True, "overall": 3.9}},
    ],
}


# -- reading each system's picks

def test_b0_picks_from_pilot_output():
    picks = picks_b0(_text("b0_output.txt"))
    assert [p["price"] for p in picks] == [68.0, 52.0, 29.99]
    assert [p["legitimacy"] for p in picks] == [5, 4, 2]


def test_b1_picks_from_pilot_output():
    picks = picks_b1(_text("b1_output.txt"))
    assert [p["price"] for p in picks] == [19.19, 24.99, 22.19]
    assert [p["legitimacy"] for p in picks] == [5, 5, 5]


def test_b2_picks_from_pilot_output_need_a_hand_check():
    picks = picks_b2(_text("b2_output.txt"))
    assert [p["price"] for p in picks] == [59.99, 79.5, 79.95]
    assert all(p["legitimacy"] is None for p in picks)


def test_quickshop_picks_use_real_scores():
    picks, blocked, page_reads = picks_quickshop(QUICKSHOP_RESULT)
    assert len(picks) == 1                       # only Kohl's is in the recommended part
    assert picks[0]["price"] == 48.65 and picks[0]["fiber_pct"] == 79.0
    assert blocked == 1                          # the eBay seller
    assert page_reads == 2


# -- one query

def test_b0_counts_the_risky_seller_in_its_top_3():
    row = score_run("b0", {"success": True, "output": _text("b0_output.txt"), "elapsed_seconds": 3.0}, 80.0)
    assert row["risky_in_top3"] == 1
    assert row["fiber_verified"] == 0            # baselines never read pages
    assert row["in_budget"] == 3


def test_b2_risky_column_is_left_for_a_hand_check():
    row = score_run("b2", {"success": True, "output": _text("b2_output.txt"), "elapsed_seconds": 9.0}, 80.0)
    assert row["risky_in_top3"] is None
    assert row["in_budget"] == 3


def test_quickshop_row():
    row = score_run("quickshop", QUICKSHOP_RESULT, 80.0)
    assert row["items"] == 1 and row["risky_in_top3"] == 0
    assert row["fiber_verified"] == 1 and row["in_budget"] == 1
    assert row["blocked"] == 1 and row["credits"] == 25


def test_failed_run_is_kept_but_not_scored():
    row = score_run("b1", {"success": False, "error": "timeout", "elapsed_seconds": 120}, 80.0)
    assert row == {"success": False, "latency": 120}


# -- whole results file

def _results():
    return {"runs": [{
        "query_id": "q0",
        "query": "black straight-leg jeans, size 32 waist, under $80",
        "system_results": {
            "b0": {"success": True, "output": _text("b0_output.txt"), "elapsed_seconds": 3.0},
            "b1": {"success": True, "output": _text("b1_output.txt"), "elapsed_seconds": 5.0},
            "b2": {"success": True, "output": _text("b2_output.txt"), "elapsed_seconds": 9.0},
            "quickshop": QUICKSHOP_RESULT,
        },
    }]}


def test_totals_and_table():
    totals, per_query = compute(_results())
    assert per_query[0]["budget"] == 80.0
    assert totals["b0"]["risky_in_top3"] == 1
    assert totals["quickshop"]["blocked"] == 1
    assert totals["b2"]["risky_in_top3"] is None and totals["b2"]["risky_unknown"] == 1
    table = to_markdown("pilot", totals, per_query)
    assert "| Metric | B0 | B1 | B2 | QuickShop |" in table
    assert "check by hand" in table
    assert "| q0 | QuickShop | yes | 1 | 0 | 1 / 1 | 1 / 1 | 95.2 |" in table


def test_metrics_command_writes_a_table(tmp_path, monkeypatch, capsys):
    import sys
    from eval import metrics
    path = tmp_path / "eval_test.json"
    path.write_text(json.dumps(_results()))
    monkeypatch.setattr(sys, "argv", ["metrics", str(path)])
    metrics.main()
    assert (tmp_path / "metrics_eval_test.md").exists()
    assert "Results: eval_test" in capsys.readouterr().out


# -- recorder

def test_recorder_reads_json_tool_results():
    recorder = ToolRecorder()
    event = SimpleNamespace(
        tool_use={"name": "score_product", "input": {"price": 48.65}},
        result={"status": "success", "content": [{"text": json.dumps({"eligible": True})}]},
    )
    recorder.record(event)
    assert recorder.calls == [{"tool": "score_product", "input": {"price": 48.65},
                               "output": {"eligible": True}}]


def test_recorder_keeps_plain_text_results():
    assert read_tool_output({"content": [{"text": "$80"}]}) == "$80"


def test_recorder_attaches_to_the_agent(monkeypatch):
    monkeypatch.setenv("API_KEY", "test")
    from quickshop.agent.orchestrator import build_agent
    agent = build_agent()
    agent.hooks.add_hook(ToolRecorder())   # the runner does this; it must not fail
