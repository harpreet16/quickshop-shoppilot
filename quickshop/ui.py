"""Streamlit cards for the activity column; no worker-thread UI calls."""

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


def render_tool_card(call):
    category, color, tone, summary = tool_presentation(call)
    with st.container(border=True):
        st.markdown(f":{color}[**{category}**]")
        st.text(call["tool"])
        args = call.get("input", {})
        subject = next((args[key] for key in ("merchant", "query", "url") if args.get(key)), None)
        if subject:
            st.text(subject)
        getattr(st, tone)(summary)
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
                for evidence in card["evidence"]:
                    st.text(f"• {evidence}")
                if card["url"]:
                    st.link_button(
                        "Demo placeholder link" if frozen else "Product page", card["url"]
                    )
