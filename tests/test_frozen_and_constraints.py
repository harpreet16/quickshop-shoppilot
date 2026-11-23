# Tests for search replay (--frozen) and for not asking what the user already said.
# They run offline: Firecrawl is replaced by a fake client.
from types import SimpleNamespace

import pytest

from quickshop.agent.interventions import KnownConstraints, find_known_constraints
from quickshop.agent.orchestrator import build_agent
from quickshop.tools import search as search_module
from quickshop.tools import search_snapshot
from quickshop.tools.search import search_listings

SEARCH_RESPONSE = {
    "success": True,
    "creditsUsed": 2,
    "data": {"web": [
        {"title": "Levi's Classic Straight Jeans", "url": "https://www.kohls.com/product/123"},
        {"title": "Old Navy Straight Jeans", "url": "https://oldnavy.gap.com/browse/456"},
    ]},
}

class FakeClient:
    calls = 0

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def post(self, url, **kwargs):
        FakeClient.calls += 1
        return SimpleNamespace(raise_for_status=lambda: None, json=lambda: SEARCH_RESPONSE)


@pytest.fixture
def snapshot_file(tmp_path, monkeypatch):
    path = tmp_path / "search_snapshot.json"
    monkeypatch.setenv("QUICKSHOP_SEARCH_SNAPSHOT", str(path))
    monkeypatch.delenv("QUICKSHOP_SEARCH_REPLAY", raising=False)
    monkeypatch.setattr(search_module.httpx, "Client", FakeClient)
    FakeClient.calls = 0
    monkeypatch.setattr(search_module, "_usage", {"calls": 0, "credits_used": 0})
    return path


# -- search replay

def test_live_search_is_saved(snapshot_file, monkeypatch):
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test")
    listings = search_listings("black jeans under $80")
    assert len(listings) == 2 and snapshot_file.exists()
    assert search_snapshot.load("black jeans under $80", 20) == listings


def test_frozen_search_gives_same_listings_without_calling_firecrawl(snapshot_file, monkeypatch):
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test")
    live = search_listings("black jeans under $80")
    monkeypatch.setenv("QUICKSHOP_SEARCH_REPLAY", "1")
    monkeypatch.delenv("FIRECRAWL_API_KEY")   # frozen mode needs no key
    frozen = search_listings("black jeans under $80")
    assert frozen == live
    assert FakeClient.calls == 1        # only the live run called Firecrawl


def test_query_spacing_and_case_do_not_matter(snapshot_file, monkeypatch):
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test")
    live = search_listings("Black  Jeans under $80 ")
    monkeypatch.setenv("QUICKSHOP_SEARCH_REPLAY", "1")
    assert search_listings("black jeans under $80") == live


def test_frozen_search_never_saved_returns_error(snapshot_file, monkeypatch):
    monkeypatch.setenv("QUICKSHOP_SEARCH_REPLAY", "1")
    result = search_listings("a query that was never run")
    assert result[0]["available"] is False and "No saved search" in result[0]["error"]
    assert FakeClient.calls == 0


def test_failed_search_is_not_saved(snapshot_file, monkeypatch):
    monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)
    result = search_listings("black jeans")
    assert result[0]["available"] is False
    assert search_snapshot.load("black jeans", 20) is None


def test_frozen_flag_turns_on_both_replays(monkeypatch):
    from quickshop.__main__ import use_frozen_mode
    monkeypatch.delenv("QUICKSHOP_SEARCH_REPLAY", raising=False)
    monkeypatch.delenv("QUICKSHOP_EVIDENCE_REPLAY", raising=False)
    use_frozen_mode()
    import os
    assert os.environ["QUICKSHOP_SEARCH_REPLAY"] == "1"
    assert os.environ["QUICKSHOP_EVIDENCE_REPLAY"] == "1"


# -- reading budget and size from the request

@pytest.mark.parametrize("text, budget", [
    ("black straight-leg jeans, size 32 waist, under $80", 80.0),
    ("linen shirt below 45 dollars", 45.0),
    ("dress up to $120.50", 120.5),
    ("cotton tee $25 or less", 25.0),
    ("wool sweater, budget of $60", 60.0),
    ("jeans for $70", 70.0),
])
def test_budget_is_found(text, budget):
    assert find_known_constraints(text)["budget"] == budget


@pytest.mark.parametrize("text, size", [
    ("black straight-leg jeans, size 32 waist, under $80", "32"),
    ("jeans 34 waist", "34"),
    ("shirt size M", "M"),
    ("chinos waist 30", "30"),
])
def test_size_is_found(text, size):
    assert find_known_constraints(text)["size"] == size


def test_nothing_found_when_not_given():
    assert find_known_constraints("black jeans") == {}


# -- the guard on ask_user

def _start(guard, text):
    guard.before_invocation(SimpleNamespace(messages=[{"role": "user", "content": [{"text": text}]}]))


def _ask(guard, question):
    event = SimpleNamespace(tool_use={"name": "ask_user", "input": {"question": question}})
    return type(guard.before_tool_call(event)).__name__


def test_budget_question_blocked_when_budget_given():
    guard = KnownConstraints()
    _start(guard, "black straight-leg jeans, size 32 waist, under $80")
    assert _ask(guard, "What is your maximum budget?") == "Deny"
    assert _ask(guard, "How much do you want to spend?") == "Deny"


def test_budget_question_allowed_when_budget_missing():
    guard = KnownConstraints()
    _start(guard, "black straight-leg jeans")
    assert _ask(guard, "What is your maximum budget?") == "Proceed"


def test_size_question_blocked_but_inseam_allowed():
    guard = KnownConstraints()
    _start(guard, "black jeans, size 32 waist")
    assert _ask(guard, "What waist size do you wear?") == "Deny"
    assert _ask(guard, "What inseam length do you need?") == "Proceed"


def test_follow_up_keeps_the_budget():
    guard = KnownConstraints()
    _start(guard, "black jeans under $80")
    _start(guard, "anything cheaper?")
    assert _ask(guard, "What is your budget?") == "Deny"


def test_other_tools_are_not_touched():
    guard = KnownConstraints()
    _start(guard, "black jeans under $80")
    search = SimpleNamespace(tool_use={"name": "search_listings", "input": {"query": "budget jeans"}})
    assert type(guard.before_tool_call(search)).__name__ == "Proceed"


def test_agent_uses_the_guard(monkeypatch):
    monkeypatch.setenv("API_KEY", "test")
    agent = build_agent()
    assert isinstance(agent.constraints, KnownConstraints)
