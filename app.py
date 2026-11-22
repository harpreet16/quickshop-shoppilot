"""Run with: streamlit run app.py --server.address 127.0.0.1"""

import sys
from queue import Empty

import streamlit as st

from quickshop.web import PILOT_QUERY, WebSession, results_to_cards

st.set_page_config(page_title="QuickShop", page_icon="🛍️")
st.title("QuickShop")
st.caption("Find clothing, compare evidence, and spot seller risks.")
st.caption("Local pilot • merchant signals are heuristics, not verified safety guarantees.")

if "shop" not in st.session_state:
    st.session_state.shop = WebSession(frozen="--frozen" in sys.argv)
    st.session_state.messages = []
    st.session_state.calls = []
    st.session_state.progress = []
    st.session_state.question = None
shop = st.session_state.shop
with st.sidebar:
    st.header("Shopping session")
    frozen = st.toggle("Frozen mode", value=shop.frozen, disabled=shop.busy)
    st.caption("Fixed synthetic demo listings; live ASU model still uses API_KEY.")
    if frozen != shop.frozen or st.button("New conversation", disabled=shop.busy):
        st.session_state.clear()
        st.session_state.shop = WebSession(frozen=frozen)
        st.session_state.messages = []
        st.session_state.calls = []
        st.session_state.progress = []
        st.session_state.question = None
        st.rerun()
    st.caption("Mode changes start a fresh conversation. Keys stay on the server.")
    st.code(PILOT_QUERY, language=None)


def render_cards(calls):
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
                if heading == "Not recommended":
                    st.error(f"Not recommended · {score.get('risk', 'unknown')} risk")
                else:
                    st.text(f"Risk: {score.get('risk', 'unknown')}")
                for evidence in card["evidence"]:
                    st.text(f"• {evidence}")
                if card["url"]:
                    st.link_button(
                        "Product page" if not shop.frozen else "Demo placeholder link", card["url"]
                    )


@st.fragment(run_every=0.5)
def conversation():
    while True:
        try:
            kind, value = shop.events.get_nowait()
        except Empty:
            break
        if kind == "question":
            st.session_state.question = value
            st.session_state.messages.append(("assistant", value))
        elif kind == "call":
            st.session_state.calls.append(value)
            name, args = value["tool"], value["input"]
            reads = sum(
                c["tool"] == "fetch_product_evidence" and not c["blocked"]
                for c in st.session_state.calls
            )
            label = {
                "search_listings": "Search completed",
                "check_merchant": f"Checked {args.get('merchant', 'seller')}",
                "fetch_product_evidence": f"Read page {reads} of 5",
                "score_product": "Product scored",
                "ask_user": "Clarification received",
            }.get(name, name)
            st.session_state.progress.append(
                label if not value["blocked"] else "Page-read budget exhausted"
            )
        elif kind in ("message", "error"):
            st.session_state.messages.append(("assistant" if kind == "message" else "error", value))
        elif kind == "done":
            st.session_state.question = None
            st.rerun()
    if shop.frozen:
        st.info(
            "Frozen demo: synthetic black-jeans data only. No SerpAPI or Firecrawl calls; model calls remain live."
        )
    for role, text in st.session_state.messages:
        with st.chat_message("assistant" if role == "error" else role):
            if role == "error":
                st.error(text)
            else:
                st.text(text)
    if st.session_state.progress:
        with st.expander("Tool progress", expanded=shop.busy):
            for label in st.session_state.progress:
                st.text(label)
    if shop.busy:
        st.info("Waiting for your reply…" if shop.waiting else "QuickShop is working…")
    render_cards(st.session_state.calls)
    prompt = st.chat_input(
        "Reply to QuickShop" if shop.waiting else "What clothing are you looking for?",
        disabled=shop.busy and not shop.waiting,
    )
    if prompt:
        st.session_state.messages.append(("user", prompt))
        if shop.waiting:
            shop.answer(prompt)
            st.session_state.question = None
        else:
            st.session_state.calls = []
            st.session_state.progress = []
            shop.start(prompt)
        st.rerun()


@st.fragment(run_every=0.5)
def page_budget():
    budget = shop.agent.budget if shop.agent else None
    st.metric("Page reads left", max(0, budget.credits - budget.used) if budget else 5)
    st.caption("Tool-call allowance per turn, not Firecrawl billing credits. Cache hits count too.")


with st.sidebar:
    page_budget()

conversation()
