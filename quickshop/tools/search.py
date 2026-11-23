# Firecrawl web discovery; product facts are verified by the evidence tool.
import os
import threading
from urllib.parse import urlparse

import httpx
from dotenv import load_dotenv
from strands import tool

from quickshop.schemas import Listing
from quickshop.tools import search_snapshot

load_dotenv()

FIRECRAWL_SEARCH_URL = "https://api.firecrawl.dev/v2/search"
_usage_lock = threading.Lock()
_usage = {"calls": 0, "credits_used": 0}


def get_search_usage() -> dict:
    with _usage_lock:
        return dict(_usage)


def _extract_listings(results: dict) -> list[dict]:
    """Map web results without guessing prices, ratings or seller identities."""
    listings = []
    seen = set()
    for item in results.get("data", {}).get("web", []):
        if not isinstance(item, dict):
            continue
        url = item.get("url")
        if not isinstance(url, str):
            continue
        try:
            parsed = urlparse(url)
            domain = (parsed.hostname or "").removeprefix("www.")
        except ValueError:
            continue
        if parsed.scheme not in ("http", "https") or not domain or url in seen:
            continue
        title = item.get("title")
        if not isinstance(title, str) or not title.strip():
            continue
        listings.append(Listing(
            title=title, price=None, merchant=domain, domain=domain, url=url,
        ).model_dump())
        seen.add(url)
    return listings


@tool
def search_listings(query: str, max_results: int = 20) -> list:
    """Search online stores for clothing using Firecrawl web search.

    Args:
        query: What to search for, for example "black straight jeans under $80".
        max_results: Maximum results, from 1 to 100 (default 20).

    Returns:
        Listings with title, merchant domain and url. Price, rating, reviews and
        thumbnail are unknown (null); use fetch_product_evidence to verify facts.
        Failures return an error with available=false.
    """
    if not query.strip() or len(query) > 500:
        return [{"error": "Query must contain 1–500 characters", "available": False}]
    if not 1 <= max_results <= 100:
        return [{"error": "max_results must be between 1 and 100", "available": False}]

    if search_snapshot.replay_on():
        saved = search_snapshot.load(query, max_results)
        if saved is None:
            return [{"error": "No saved search for this query. Run it once without --frozen first.", "available": False}]
        return saved

    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        return [{"error": "FIRECRAWL_API_KEY not configured", "available": False}]

    try:
        with _usage_lock:
            _usage["calls"] += 1
        with httpx.Client(timeout=65.0) as client:
            response = client.post(
                FIRECRAWL_SEARCH_URL,
                headers={"Authorization": f"Bearer {api_key}"},
                json={"query": query, "limit": max_results, "sources": ["web"],
                      "country": "US", "timeout": 60000},
            )
            response.raise_for_status()
            data = response.json()

        if data.get("success") is not True:
            return [{"error": "Firecrawl search failed", "available": False}]
        credits = data.get("creditsUsed")
        if isinstance(credits, int) and credits >= 0:
            with _usage_lock:
                _usage["credits_used"] += credits

        listings = _extract_listings(data)[:max_results]
        if not listings:
            return [{"error": "No listings found for this query", "available": False}]
        try:
            search_snapshot.save(query, max_results, listings)
        except OSError:
            pass
        return listings
    except httpx.TimeoutException:
        return [{"error": "Search timed out", "available": False}]
    except httpx.HTTPStatusError as exc:
        return [{"error": f"HTTP error: {exc.response.status_code}", "available": False}]
    except Exception:
        # Do not expose provider responses or request headers containing credentials.
        return [{"error": "Search unavailable", "available": False}]
