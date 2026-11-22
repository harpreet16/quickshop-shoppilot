# Turns eval/results/*.json (from eval/runner.py) into one results table per file.
#
# Run:  python -m eval.metrics                      (newest results file)
#       python -m eval.metrics eval/results/a.json eval/results/b.json
#
# Where the numbers come from:
# - QuickShop: the real score_product and page-read results saved by the runner.
# - B0 and B1: read from their fixed output format ("legitimacy=5", "Legitimacy Score: 5").
# - B2: writes free text, so its legitimacy column says "check by hand".
# "Fabric verified" only counts a natural fiber share read from the product page by a page read.
# The baselines never read pages, so theirs is always 0.
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from quickshop.agent.interventions import find_known_constraints

SYSTEMS = ["b0", "b1", "b2", "quickshop"]
SYSTEM_NAMES = {"b0": "B0", "b1": "B1", "b2": "B2", "quickshop": "QuickShop"}
# model or API calls each baseline makes per query, fixed by how it is built
BASELINE_CALLS = {"b0": 1, "b1": 2, "b2": 1}
LEGIT_GATE = 3
NATURAL_FIBER_MAJORITY = 50

_MONEY = r"\$\s*([\d,]+(?:\.\d{1,2})?)"


def _money(text):
    return float(text.replace(",", ""))


# -- reading each system's picks: a list of {"price": float|None, "legitimacy": int|None}

def picks_b0(output):
    section = re.split(r"#+\s*Recommended products", output, flags=re.I)
    if len(section) < 2:
        return []
    section = re.split(r"#+\s*Rejected", section[1], flags=re.I)[0]
    picks = []
    for block in re.split(r"\n\s*(?=\d+\.\s)", "\n" + section):
        if not re.match(r"\s*\d+\.\s", block):
            continue
        price = re.search(_MONEY, block)
        # \s also matches the odd spaces LLMs write, like the narrow no-break space
        legit = re.search(r"Legitimacy\s*Score:\s*(\d)", block, re.I)
        picks.append({"price": _money(price.group(1)) if price else None,
                      "legitimacy": int(legit.group(1)) if legit else None})
    return picks


def picks_b1(output):
    section = re.split(r"Top \d+ recommendations", output, flags=re.I)
    if len(section) < 2:
        return []
    section = re.split(r"Not recommended", section[1], flags=re.I)[0]
    picks = []
    for block in re.split(r"\n\s*(?=\d+\.\s)", "\n" + section):
        if not re.match(r"\s*\d+\.\s", block):
            continue
        price = re.search(r"\(" + _MONEY + r"\)", block)
        legit = re.search(r"legitimacy=(\d)", block)
        picks.append({"price": _money(price.group(1)) if price else None,
                      "legitimacy": int(legit.group(1)) if legit else None})
    return picks


def picks_b2(output):
    picks = []
    for block in re.split(r"\n(?=#+\s*\d+\.)", output)[1:]:
        price = re.search(r"\*\*Price:\*\*\s*" + _MONEY, block)
        # B2 describes the seller in words, not a score, so this needs a hand check
        picks.append({"price": _money(price.group(1)) if price else None, "legitimacy": None})
    return picks


def _recommended_section(output):
    # everything before the "Not recommended" part of QuickShop's answer
    return re.split(r"not recommended", output, flags=re.I)[0]


def _price_strings(price):
    strings = {f"${price:,.2f}", f"${price:.2f}"}
    if float(price).is_integer():
        strings.add(f"${price:.0f}")
    return strings


def _same_url(a, b):
    try:
        from quickshop.evidence.cache import canonicalize_url
        return canonicalize_url(a) == canonicalize_url(b)
    except (ValueError, ImportError):
        return a == b


def picks_quickshop(result):
    """QuickShop's picks with their real scores.

    A scored item counts as recommended when its price appears in the recommended part
    of the final answer (before "Not recommended").
    """
    log = result.get("tool_log") or []
    scored = [(c["input"], c["output"]) for c in log
              if c["tool"] == "score_product" and isinstance(c["output"], dict)]
    pages = [c["output"] for c in log
             if c["tool"] == "fetch_product_evidence" and isinstance(c["output"], dict)]
    recommended_text = _recommended_section(result.get("output", ""))

    picks, seen = [], set()
    for given, scores in scored:
        price = given.get("price")
        if price is None or price in seen:
            continue
        if not any(s in recommended_text for s in _price_strings(float(price))):
            continue
        seen.add(price)
        url = given.get("url") or scores.get("url") or ""
        fiber = None
        for page in pages:
            if page.get("natural_fiber_pct") is not None and _same_url(page.get("url", ""), url):
                fiber = page["natural_fiber_pct"]
        picks.append({"price": float(price), "legitimacy": scores.get("legitimacy"),
                      "eligible": scores.get("eligible"), "fiber_pct": fiber})
    blocked = sum(1 for _, s in scored if s.get("eligible") is False)
    page_reads = sum(1 for c in log if c["tool"] == "fetch_product_evidence")
    return picks, blocked, page_reads


# -- one query

def score_run(system, result, budget):
    """Numbers for one system on one query. None means "not known, check by hand"."""
    row = {"success": bool(result.get("success")), "latency": result.get("elapsed_seconds")}
    if not row["success"]:
        return row
    output = result.get("output", "")
    if system == "quickshop":
        picks, blocked, page_reads = picks_quickshop(result)
        row.update(blocked=blocked, page_reads=page_reads,
                   tool_calls=result.get("tool_calls"), credits=result.get("firecrawl_credits"))
        verified = sum(1 for p in picks[:3] if (p["fiber_pct"] or 0) >= NATURAL_FIBER_MAJORITY)
    else:
        picks = {"b0": picks_b0, "b1": picks_b1, "b2": picks_b2}[system](output)
        row.update(blocked=None, page_reads=0, tool_calls=BASELINE_CALLS[system], credits=0)
        verified = 0
    top3 = picks[:3]
    legit_known = all(p["legitimacy"] is not None for p in top3)
    row["items"] = len(picks)
    row["risky_in_top3"] = (sum(1 for p in top3 if p["legitimacy"] < LEGIT_GATE)
                            if legit_known else None)
    row["fiber_verified"] = verified
    row["top3"] = len(top3)
    if budget is not None and all(p["price"] is not None for p in top3):
        row["in_budget"] = sum(1 for p in top3 if p["price"] <= budget)
    else:
        row["in_budget"] = None
    return row


# -- one results file

def compute(results):
    """Returns {system: totals} and the per-query rows."""
    per_query = []
    for run in results.get("runs", []):
        budget = find_known_constraints(run["query"]).get("budget")
        rows = {system: score_run(system, res, budget)
                for system, res in run.get("system_results", {}).items() if system in SYSTEMS}
        per_query.append({"id": run.get("query_id"), "query": run["query"], "budget": budget, "rows": rows})

    totals = {}
    for system in SYSTEMS:
        rows = [q["rows"][system] for q in per_query if system in q["rows"]]
        if not rows:
            continue
        ok = [r for r in rows if r["success"]]

        def total(key, rows=ok):
            values = [r[key] for r in rows if r.get(key) is not None]
            return sum(values) if values else None

        def average(key, rows=ok):
            values = [r[key] for r in rows if r.get(key) is not None]
            return round(sum(values) / len(values), 1) if values else None

        unknown_risky = sum(1 for r in ok if r.get("risky_in_top3") is None)
        budget_rows = [r for r in ok if r.get("in_budget") is not None]
        totals[system] = {
            "queries": len(rows),
            "succeeded": len(ok),
            "risky_in_top3": total("risky_in_top3"),
            "risky_unknown": unknown_risky,
            "blocked": total("blocked"),
            "fiber_verified": total("fiber_verified"),
            "top3_picks": total("top3"),
            "in_budget": total("in_budget", budget_rows),
            "budget_picks": total("top3", budget_rows),
            "avg_items": average("items"),
            "avg_tool_calls": average("tool_calls"),
            "avg_page_reads": average("page_reads"),
            "credits": total("credits"),
            "avg_latency": average("latency", rows),
        }
    return totals, per_query


def _cell(value, unknown="check by hand"):
    return unknown if value is None else str(value)


def to_markdown(name, totals, per_query):
    systems = [s for s in SYSTEMS if s in totals]
    header = "| Metric | " + " | ".join(SYSTEM_NAMES[s] for s in systems) + " |"
    line = "|---" * (len(systems) + 1) + "|"

    def row(label, fn):
        return f"| {label} | " + " | ".join(fn(totals[s]) for s in systems) + " |"

    def risky(t):
        if t["risky_in_top3"] is None:
            return "check by hand"
        extra = f" (+{t['risky_unknown']} to check)" if t["risky_unknown"] else ""
        return f"{t['risky_in_top3']}{extra}"

    lines = [
        f"## Results: {name}", "",
        f"{len(per_query)} {'query' if len(per_query) == 1 else 'queries'}. "
        "Picks are counted over each system's top 3.", "",
        header, line,
        row("Queries that ran", lambda t: f"{t['succeeded']} / {t['queries']}"),
        row("Risky seller in top 3 (legitimacy below 3)", risky),
        row("Blocked by the legitimacy gate", lambda t: _cell(t["blocked"], "no gate")),
        row("Fabric verified from the page", lambda t: f"{t['fiber_verified'] or 0} / {t['top3_picks'] or 0}"),
        row("Within budget", lambda t: f"{t['in_budget']} / {t['budget_picks']}" if t["in_budget"] is not None else "n/a"),
        row("Items recommended (average)", lambda t: _cell(t["avg_items"])),
        row("Tool calls (average)", lambda t: _cell(t["avg_tool_calls"])),
        row("Page reads (average)", lambda t: _cell(t["avg_page_reads"])),
        row("Firecrawl credits (total)", lambda t: _cell(t["credits"], "not recorded")),
        row("Seconds per query (average)", lambda t: _cell(t["avg_latency"])),
        "",
        "### Per query (for the hand check)", "",
        "| Query | System | Ran | Items | Risky in top 3 | Fabric verified | Within budget | Seconds |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for q in per_query:
        for system in systems:
            r = q["rows"].get(system)
            if r is None:
                continue
            if not r["success"]:
                lines.append(f"| {q['id']} | {SYSTEM_NAMES[system]} | failed | | | | | {_cell(r['latency'], '')} |")
                continue
            lines.append(
                f"| {q['id']} | {SYSTEM_NAMES[system]} | yes | {r['items']} | {_cell(r['risky_in_top3'])} | "
                f"{r['fiber_verified']} / {r['top3']} | "
                f"{'n/a' if r['in_budget'] is None else str(r['in_budget']) + ' / ' + str(r['top3'])} | "
                f"{_cell(r['latency'], '')} |"
            )
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Results tables from eval/results/*.json")
    parser.add_argument("files", nargs="*", help="results files (default: the newest one in eval/results)")
    args = parser.parse_args()

    files = [Path(f) for f in args.files]
    if not files:
        found = sorted(Path("eval/results").glob("eval_*.json"))
        if not found:
            print("No results yet. Run: python -m eval.runner")
            return
        files = [found[-1]]

    for path in files:
        totals, per_query = compute(json.loads(path.read_text()))
        table = to_markdown(path.stem, totals, per_query)
        print(table)
        out = path.with_name(f"metrics_{path.stem}.md")
        out.write_text(table)
        print(f"Saved to {out}\n")


if __name__ == "__main__":
    main()
