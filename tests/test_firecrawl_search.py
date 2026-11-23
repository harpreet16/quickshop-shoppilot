"""Offline contract tests for Firecrawl v2 discovery and its B1 caller."""
import httpx
import pytest

from quickshop.tools import search
from quickshop.tools.search import search_listings


@pytest.fixture
def api(monkeypatch, tmp_path):
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test-only")
    monkeypatch.delenv("QUICKSHOP_SEARCH_REPLAY", raising=False)
    monkeypatch.setenv("QUICKSHOP_SEARCH_SNAPSHOT", str(tmp_path / "search.json"))
    monkeypatch.setattr(search, "_usage", {"calls": 0, "credits_used": 0})
    calls = []

    def install(payload=None, status=200, error=None):
        def respond(request):
            calls.append(request)
            if error:
                raise error
            return httpx.Response(status, json=payload)
        transport = httpx.MockTransport(respond)
        client = httpx.Client
        monkeypatch.setattr(search.httpx, "Client", lambda **kw: client(transport=transport, **kw))
    return install, calls


def test_request_contract_limit_and_usage(api):
    import json
    install, calls = api
    install({"success": True, "creditsUsed": 2, "data": {"web": [
        {"title": "Jeans", "url": "https://store.test/p"},
        {"title": "Other", "url": "https://store.test/q"},
    ]}})
    assert len(search_listings("black jeans", max_results=1)) == 1
    request, = calls
    assert str(request.url) == search.FIRECRAWL_SEARCH_URL
    assert request.method == "POST"
    assert request.headers["Authorization"] == "Bearer test-only"
    assert json.loads(request.content) == {
        "query": "black jeans", "limit": 1, "sources": ["web"],
        "country": "US", "timeout": 60000,
    }
    assert search.get_search_usage() == {"calls": 1, "credits_used": 2}


@pytest.mark.parametrize("payload,status,error,message", [
    ({"success": False, "error": "private provider detail"}, 200, None, "Firecrawl search failed"),
    ({"success": True, "data": {"web": []}}, 200, None, "No listings found"),
    ({}, 401, None, "HTTP error: 401"),
    ({}, 402, None, "HTTP error: 402"),
    ({}, 429, None, "HTTP error: 429"),
    ({}, 500, None, "HTTP error: 500"),
    (None, 200, httpx.ReadTimeout("private request detail"), "Search timed out"),
    (None, 200, RuntimeError("secret test-only"), "Search unavailable"),
    ({"success": True, "data": None}, 200, None, "Search unavailable"),
])
def test_failures_are_safe_and_not_cached(api, payload, status, error, message):
    from quickshop.tools import search_snapshot
    install, _ = api
    install(payload, status, error)
    result, = search_listings("jeans")
    assert result["available"] is False
    assert message in result["error"]
    assert "private" not in result["error"] and "test-only" not in result["error"]
    assert search_snapshot.load("jeans", 20) is None


@pytest.mark.parametrize("query,limit", [(" ", 20), ("x" * 501, 20), ("jeans", 0), ("jeans", 101)])
def test_invalid_input_never_calls_api(api, query, limit):
    _, calls = api
    assert search_listings(query, max_results=limit)[0]["available"] is False
    assert calls == []


def test_b1_uses_shared_search_and_preserves_unknowns(api):
    from baselines.b1.run import search_listings as baseline_search
    install, calls = api
    install({"success": True, "data": {"web": [{"title": "Jeans", "url": "https://store.test/p"}]}})
    result, = baseline_search("jeans")
    assert result["link"] == result["url"] == "https://store.test/p"
    assert result["price"] is None and result["rating"] is None
    assert len(calls) == 1


def test_b1_search_failure_does_not_reach_scoring(api):
    from baselines.b1.run import search_listings as baseline_search
    install, _ = api
    install({}, status=402)
    with pytest.raises(RuntimeError, match="HTTP error: 402"):
        baseline_search("jeans")


def test_usage_includes_search_without_mutating_evidence_counter(api, monkeypatch):
    from quickshop.evidence import tool
    from types import SimpleNamespace
    install, _ = api
    install({"success": True, "creditsUsed": 2, "data": {"web": []}})
    search_listings("jeans")
    monkeypatch.setattr(tool, "get_service", lambda: SimpleNamespace(usage=lambda: {
        "firecrawl": {"calls": 1, "credits_used": 5}, "cache": {},
    }))
    assert tool.get_usage()["firecrawl"] == {"calls": 2, "credits_used": 7}
    assert tool.get_usage()["firecrawl"] == {"calls": 2, "credits_used": 7}



def test_report_handles_unknown_search_prices():
    from quickshop.report import render_report
    report = render_report("jeans", [{"title": "Jeans", "price": None}],
                           warnings=[{"title": "Other jeans", "price": None}])
    assert "Price: unknown" in report
    assert "price unknown" in report
    assert "$0.00" not in report
