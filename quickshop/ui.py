"""Streamlit cards for the activity column; no worker-thread UI calls."""

from html import escape
from urllib.parse import urlsplit

import streamlit as st

from quickshop.web import result_data, results_to_cards

CATEGORIES = {
    "search_listings": ("Search", "blue"),
    "check_merchant": ("Merchant", "orange"),
    "fetch_product_evidence": ("Evidence", "violet"),
    "score_product": ("Scoring", "green"),
    "ask_user": ("Clarification", "gray"),
    "show_results": ("Results", "violet"),
}


UI_STYLES = """
<style>
.stMainBlockContainer {padding-top: 3.5rem; padding-bottom: 1rem;}
.st-key-activity-feed [data-testid="stVerticalBlock"] {gap: .25rem;}
.st-key-activity-feed [data-testid="stVerticalBlockBorderWrapper"] {padding: .5rem;}
.st-key-activity-feed [data-testid="stAlert"] {padding: .35rem .5rem;}
.st-key-activity-feed [data-testid="stExpander"] summary {padding: .25rem .5rem; min-height: 1.7rem;}
.qs-tool {display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.5fr); gap: 0 .5rem; font-size: .8rem; line-height: 1.3; border-left: 3px solid; padding-left: .5rem;}
.qs-tool span {text-align: right; overflow-wrap: anywhere; font-size: .75rem;}
.qs-tool small {grid-column: 1 / -1; display: block; color: var(--text-color); overflow: hidden;
  text-overflow: ellipsis; white-space: nowrap; opacity: .8;}
.qs-info {color: var(--blue-text-color, #2864b4);}
.qs-warning {color: var(--orange-text-color, #a65b00);}
.qs-error {color: var(--red-text-color, #b42318);}
.qs-success {color: var(--green-text-color, #16803c);}
.qs-summary {font-size: .75rem;}
.qs-summary table {width: 100%; border-collapse: collapse;}
.qs-summary th {text-align: left;}
.qs-summary td, .qs-summary th {padding: .2rem .35rem; border-bottom: 1px solid #8883;}
.qs-summary td:nth-child(2) {max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;}
@media (max-width: 1200px) {
  .qs-summary td:first-child, .qs-summary th:first-child {display: none;}
  .qs-summary table {table-layout: fixed;}
  .qs-summary td:nth-child(2) {width: 45%;}
}
.qs-options {font-size: .75rem;}
.qs-options table {width: 100%; table-layout: fixed; border-collapse: collapse;}
.qs-options th {text-align: left;}
.qs-options td, .qs-options th {padding: .35rem; border-bottom: 1px solid #8883; vertical-align: top; overflow-wrap: anywhere;}
.qs-options .qs-link {display: inline-block; padding: .05rem .3rem; font-size: .7rem; border: 1px solid currentColor;
  border-radius: 999px; text-decoration: none; white-space: nowrap;}
.qs-options .qs-link:focus-visible {outline: 2px solid currentColor; outline-offset: 2px;}
</style>
"""


def tool_presentation(call):
    category, color = CATEGORIES.get(call["tool"], ("Tool", "gray"))
    tone, summary = "info", "Completed"
    data = result_data(call)
    if call.get("status") == "running":
        summary = "Waiting for your reply" if call["tool"] == "ask_user" else "Running…"
    elif call.get("blocked"):
        tone, summary = "warning", "Blocked · page-read budget exhausted"
    elif call.get("status") != "success":
        tone, summary = "error", "Tool failed"
    elif isinstance(data, list) and any(
        isinstance(item, dict) and item.get("error") for item in data
    ):
        tone, summary = "error", "Search unavailable"
    elif isinstance(data, dict):
        if data.get("eligible") is False:
            tone, summary = (
                "error",
                "Not recommended · " + str(data.get("risk") or "unknown") + " risk",
            )
        elif (
            data.get("error")
            or data.get("status") == "unavailable"
            or data.get("available") is False
        ):
            tone, summary = "error", "Unavailable"
        elif data.get("risk"):
            risk = data["risk"]
            tone, summary = (
                {"low": "success", "medium": "warning", "high": "error"}.get(risk, "info"),
                f"{risk} risk",
            )
        elif data.get("status") == "partial" or data.get("known_brand") is False:
            tone, summary = (
                "warning",
                "Incomplete evidence" if category == "Evidence" else "Unrecognized seller",
            )
    return category, color, tone, summary


def tool_subject(call):
    args = call.get("input", {})
    data = result_data(call)
    if isinstance(data, dict) and data.get("merchant"):
        return str(data["merchant"])
    for key in ("merchant", "query", "url"):
        if args.get(key):
            return str(args[key])
    return call["tool"]


def event_summary_html(calls):
    rows = []
    for call in calls[-10:][::-1]:
        category, _, tone, summary = tool_presentation(call)
        cells = "".join(
            f"<td>{escape(value)}</td>" for value in (category, tool_subject(call), summary)
        )
        rows.append(f'<tr class="qs-{tone}">{cells}</tr>')
    return (
        '<div class="qs-summary"><table aria-label="Live event summary">'
        "<thead><tr><th>Type</th><th>Subject</th><th>Event</th></tr></thead>"
        "<tbody>" + "".join(rows) + "</tbody></table></div>"
    )


def options_table_html(calls):
    listings, evidence, scored = {}, {}, set()
    for call in calls:
        data = result_data(call)
        if call["tool"] == "search_listings" and isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and isinstance(item.get("url"), str):
                    listings[item["url"]] = item
        elif isinstance(data, dict) and data.get("url"):
            if call["tool"] == "fetch_product_evidence":
                evidence[data["url"]] = data
            elif call["tool"] == "score_product":
                scored.add(data["url"])
    recommended, rejected = results_to_cards(calls)
    verdicts = {card["url"]: ("success", "Recommended") for card in recommended}
    verdicts.update({card["url"]: ("error", "Not recommended") for card in rejected})
    rows = []
    for url, item in listings.items():
        facts = evidence.get(url, {})
        brand = facts.get("brand") or item.get("brand") or "—"
        title = item.get("title") or facts.get("title") or "Unknown product"
        tone, verdict = verdicts.get(
            url, ("info", "Awaiting verdict" if url in scored else "Not reviewed")
        )
        try:
            parsed = urlsplit(url)
            safe = parsed.scheme in ("https", "http") and bool(parsed.netloc)
        except ValueError:
            safe = False
        link = (
            f'<a class="qs-link" href="{escape(url, quote=True)}" target="_blank" '
            f'rel="noopener noreferrer" aria-label="Open product: {escape(str(title), quote=True)}">Open</a>'
            if safe
            else "—"
        )
        rows.append(
            f"<tr><td>{escape(str(brand))}</td><td>{escape(str(title))}</td>"
            f'<td>{link}</td><td class="qs-{tone}">{escape(verdict)}</td></tr>'
        )
    return (
        '<div class="qs-options"><table aria-label="Options">'
        '<colgroup><col style="width:18%"><col style="width:36%">'
        '<col style="width:16%"><col style="width:30%"></colgroup>'
        "<thead><tr><th>Brand</th><th>Title</th><th>Link</th><th>Verdict</th></tr></thead>"
        "<tbody>"
        + ("".join(rows) or '<tr><td colspan="4">No options found yet.</td></tr>')
        + "</tbody></table></div>"
    )


def render_tool_card(call):
    category, color, tone, summary = tool_presentation(call)
    with st.container(border=True):
        st.html(
            f'<div class="qs-tool qs-{tone}"><strong style="color:{color}">{escape(category)}</strong>'
            f'<span>{escape(summary)}</span><small title="{escape(tool_subject(call), quote=True)}">'
            f"{escape(tool_subject(call))}</small></div>"
        )
        with st.expander("Input and output"):
            st.caption("Input")
            st.json(call.get("input", {}))
            st.caption("Output")
            if call.get("status") == "running":
                st.text("Pending…")
            else:
                data = result_data(call)
                st.json(data if data is not None else call.get("result", {}))


def render_product_cards(calls, frozen=False):
    recommended, rejected = results_to_cards(calls)
    for heading, cards in (("Recommendations", recommended), ("Not recommended", rejected)):
        if not cards:
            continue
        st.subheader(heading)
        for card in cards:
            with st.container(border=True):
                st.text(card["title"])
                st.text(
                    f"Price: {card['price'] if card['price'] is not None else 'unknown'} USD · {card['merchant']}"
                )
                score = card["scores"]
                st.text(
                    f"P/Q/L: {score.get('price', '?')} / {score.get('quality', '?')} / "
                    f"{score.get('legitimacy', '?')} out of 5 · Overall: {score.get('overall', '?')}"
                )
                risk = score.get("risk") or "unknown"
                tone = (
                    "error"
                    if heading == "Not recommended"
                    else {"low": "success", "medium": "warning", "high": "error"}.get(risk, "info")
                )
                getattr(st, tone)(
                    f"{'Not recommended · ' if heading == 'Not recommended' else ''}{risk} risk"
                )
                with st.expander("Evidence"):
                    for evidence in card["evidence"]:
                        st.text(f"• {evidence}")
                if card["url"]:
                    st.link_button(
                        "Demo placeholder link" if frozen else "Product page", card["url"]
                    )
