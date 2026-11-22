import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

pytest.importorskip("fastapi")
pytest.importorskip("sse_starlette")

from fastapi.testclient import TestClient  # noqa: E402

from backend.api.main import app  # noqa: E402
from quickshop.config import GEMINI_MODEL_ID, MODEL_ID  # noqa: E402

KEYS = ("SERPAPI_KEY", "FIRECRAWL_API_KEY", "GEMINI_API_KEY", "API_KEY")


@pytest.fixture
def client(monkeypatch):
    for key in KEYS:
        monkeypatch.delenv(key, raising=False)
    return TestClient(app)


def test_health_reports_gemini_when_its_key_is_set(client, monkeypatch):
    for key in ("SERPAPI_KEY", "FIRECRAWL_API_KEY", "GEMINI_API_KEY"):
        monkeypatch.setenv(key, "x")

    body = client.get("/health").json()

    assert body["status"] == "ok"
    assert body["model"] == GEMINI_MODEL_ID
    assert body["services"] == {"serpapi": True, "firecrawl": True, "model": True}


def test_health_reports_asu_model_when_only_the_asu_key_is_set(client, monkeypatch):
    for key in ("SERPAPI_KEY", "FIRECRAWL_API_KEY", "API_KEY"):
        monkeypatch.setenv(key, "x")

    body = client.get("/health").json()

    assert body["status"] == "ok"
    assert body["model"] == MODEL_ID
    assert body["services"]["model"] is True


def test_health_is_degraded_and_names_what_is_missing(client, monkeypatch):
    monkeypatch.setenv("SERPAPI_KEY", "x")

    body = client.get("/health").json()

    assert body["status"] == "degraded"
    assert body["services"] == {"serpapi": True, "firecrawl": False, "model": False}


def test_cors_allows_the_frontend_origin(client):
    response = client.options(
        "/chat",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
