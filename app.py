"""Run with: streamlit run app.py --server.address 127.0.0.1"""

import sys
from queue import Empty

import streamlit as st

from quickshop.ui import (
    UI_STYLES,
    event_summary_html,
    options_table_html,
    render_product_cards,
    render_tool_card,
)
from quickshop.web import PILOT_QUERY, WebSession

st.set_page_config(page_title="QuickShop", page_icon="🛍️", layout="wide")
st.html(UI_STYLES)
st.title("QuickShop")
st.caption("Find clothing, compare evidence, and spot seller risks.")
st.caption("Local pilot • merchant signals are heuristics, not verified safety guarantees.")

if "shop" not in st.session_state:
    st.session_state.shop = WebSession(frozen="--frozen" in sys.argv)
    st.session_state.messages = []
    st.session_state.calls = []
    st.session_state.question = None
st.session_state.setdefault("running_tools", {})
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
        st.session_state.running_tools = {}
        st.session_state.question = None
        st.rerun()
    st.caption("Mode changes start a fresh conversation. Keys stay on the server.")
    st.code(PILOT_QUERY, language=None)


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
        elif kind == "tool_start":
            st.session_state.running_tools[value["tool_id"]] = value
        elif kind == "call":
            st.session_state.running_tools.pop(value.get("tool_id"), None)
            st.session_state.calls.append(value)
        elif kind in ("message", "error"):
            st.session_state.messages.append(("assistant" if kind == "message" else "error", value))
        elif kind == "done":
            st.session_state.question = None
            st.session_state.running_tools = {}
            st.rerun()

    chat, activity = st.columns([3, 2], gap="large")
    with chat:
        st.subheader("Conversation")
        if shop.frozen:
            st.info(
                "Frozen demo: synthetic black-jeans data. Only the ASU model makes live API calls."
            )
        with st.container(height=600, border=False, key="conversation-feed", autoscroll=True):
            for role, text in st.session_state.messages:
                with st.chat_message("assistant" if role == "error" else role):
                    if role == "error":
                        st.error(text)
                    else:
                        st.text(text)
            st.caption("Latest events")
            st.html(
                event_summary_html(
                    [*st.session_state.calls, *st.session_state.running_tools.values()]
                )
            )
            st.caption("Options")
            st.html(options_table_html(st.session_state.calls))
            if shop.busy:
                st.info("Waiting for your reply…" if shop.waiting else "QuickShop is working…")
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
                st.session_state.running_tools = {}
                shop.start(prompt)
            st.rerun()
    with activity:
        st.subheader("Live activity")
        with st.container(height=600, border=False, key="activity-feed", autoscroll=True):
            if not st.session_state.calls and not st.session_state.running_tools:
                st.info("Tool activity will appear here when you start shopping.")
            for call in st.session_state.calls:
                render_tool_card(call)
            for call in st.session_state.running_tools.values():
                render_tool_card(call)
            render_product_cards(st.session_state.calls, frozen=shop.frozen)


@st.fragment(run_every=0.5)
def page_budget():
    budget = shop.agent.budget if shop.agent else None
    st.metric("Page reads left", max(0, budget.credits - budget.used) if budget else 5)
    st.caption("Tool-call allowance per turn, not Firecrawl billing credits. Cache hits count too.")


with st.sidebar:
    page_budget()

conversation()
