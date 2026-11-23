# search_listings using SerpAPI Google Shopping
# Each shopping_results item only gives a google.com/search?ibp=oshop URL — not a real product
# page. We call serpapi_product_api for the top-scored candidates to get actual retailer URLs
# from the "stores" list, so Firecrawl can scrape them.
import math
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional
from urllib.parse import urlparse

from dotenv import load_dotenv
from strands import tool
import httpx

from quickshop.schemas import Listing
from quickshop.tools import search_snapshot

load_dotenv()

SERPAPI_BASE = "https://serpapi.com/search"

# How many product-API calls to fire in parallel.
_PRODUCT_API_WORKERS = 5

# Max product-API calls per search_listings call. Each costs 1 SerpAPI credit.
# We score candidates first and only spend credits on the most promising ones.
_PRODUCT_API_LIMIT = 10

# Quick brand check — avoids a circular import with merchant.py.
# Used only for scoring; the full KNOWN_BRANDS list is still in merchant.py.
_KNOWN_MERCHANTS = {
    "walmart", "amazon", "target", "nordstrom", "macy's", "macys", "bloomingdales",
    "kohl's", "kohls", "gap", "old navy", "uniqlo", "zara", "h&m", "hm", "asos",
    "levi's", "levis", "wrangler", "nike", "adidas", "lululemon", "patagonia",
    "madewell", "everlane", "banana republic", "j.crew", "jcrew", "free people",
    "anthropologie", "urban outfitters", "boot barn", "carhartt", "ralph lauren",
    "tommy hilfiger", "calvin klein", "zappos", "revolve", "rei",
}


def _thumbnail(item: dict) -> Optional[str]:
    value = item.get("thumbnail")
    return value if isinstance(value, str) and value.startswith(("http://", "https://")) else None


def _parse_price(raw) -> float:
    if isinstance(raw, (int, float)):
        return float(raw)
    if isinstance(raw, str):
        cleaned = raw.replace("$", "").replace(",", "").strip()
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    return 0.0


def _candidate_score(item: dict, position: int) -> float:
    """
    Score a shopping_results item using signals available before the product API call.
    Higher score = more worth spending a product API credit on.

    Signals used (in order of weight):
      1. multiple_sources   — product has several retailers; one call yields 2–3 listings
      2. rating × log(reviews) — proven buyer interest, not a ghost listing
      3. known merchant     — recognised brand is more likely to have a scrapeable page
      4. google position    — Google's own relevance ranking as a tie-breaker
      5. price plausibility — suspiciously cheap items are penalised
    """
    score = 0.0

    # 1. multiple_sources: each product API call returns 2–3 stores instead of 1
    if item.get("multiple_sources"):
        score += 3.0

    # 2. Social proof: rating × log10(reviews + 1)
    #    4.5★ × 1 000 reviews → 4.5 × 3.0 = 13.5
    #    4.5★ × 10 reviews   → 4.5 × 1.04 = 4.7
    #    No rating            → 0
    rating = item.get("rating") or 0.0
    reviews = item.get("reviews") or 0
    if rating > 0:
        score += rating * math.log10(reviews + 1)

    # 3. Known merchant: recognised brands have real, scrapeable product pages
    source = (item.get("source") or "").lower().strip().rstrip("'s")
    if any(known in source or source in known for known in _KNOWN_MERCHANTS):
        score += 2.0

    # 4. Google position: gentle decreasing bonus (position 1 → +1.0, position 20 → +0.05)
    score += max(0.0, 1.0 - position * 0.05)

    # 5. Price plausibility: penalise anything under $5 (likely counterfeit/clickbait)
    price = item.get("extracted_price") or 0.0
    if 0 < price < 5.0:
        score -= 3.0

    return score


def _fetch_stores(product_api_url: str, api_key: str) -> list[dict]:
    """Call serpapi_product_api and return stores that have a real http(s) URL.

    Retries up to 3 times with exponential backoff on 429 (rate limit) responses.
    The api_key is appended directly to the URL — httpx params= does not merge
    correctly with the existing query string on this endpoint.
    """
    full_url = f"{product_api_url}&api_key={api_key}"
    for attempt in range(3):
        try:
            with httpx.Client(timeout=15.0) as client:
                r = client.get(full_url)
            if r.status_code == 429:
                time.sleep(2 ** attempt)   # 1s → 2s → 4s
                continue
            r.raise_for_status()
            stores = r.json().get("product_results", {}).get("stores", [])
            return [s for s in stores
                    if isinstance(s.get("link"), str) and s["link"].startswith("http")]
        except Exception:
            if attempt == 2:
                return []
            time.sleep(1)
    return []


def _extract_listings(results: dict, api_key: str = "") -> list[dict]:
    """
    Build Listing objects from SerpAPI shopping_results.

    Step 1 — Score every candidate using cheap listing-level signals (no API calls).
    Step 2 — Call serpapi_product_api only for the top _PRODUCT_API_LIMIT candidates.
             Each call returns real retailer URLs (walmart.com, wrangler.com, …).
    Step 3 — Create one Listing per retailer store (up to 3 per product).

    Fallback: items without serpapi_product_api (e.g. test fixtures with plain links)
    fall back to their own link field, so offline tests stay green.
    """
    shopping_results = results.get("shopping_results", [])
    if not shopping_results:
        return []

    # --- Step 1: score and select top candidates ---
    candidates = [
        (item, _candidate_score(item, pos), item["serpapi_product_api"])
        for pos, item in enumerate(shopping_results)
        if item.get("serpapi_product_api")
    ]
    candidates.sort(key=lambda x: x[1], reverse=True)
    top_candidates = candidates[:_PRODUCT_API_LIMIT]

    # --- Step 2: parallel product-API calls for top candidates only ---
    store_map: dict[str, list[dict]] = {}
    if top_candidates and api_key:
        with ThreadPoolExecutor(max_workers=_PRODUCT_API_WORKERS) as pool:
            future_to_id = {
                pool.submit(_fetch_stores, url, api_key): item.get("product_id", str(i))
                for i, (item, _score, url) in enumerate(top_candidates)
            }
            for future in as_completed(future_to_id):
                pid = future_to_id[future]
                try:
                    store_map[pid] = future.result()
                except Exception:
                    store_map[pid] = []

    # --- Step 3: build listings ---
    listings: list[dict] = []
    for item in shopping_results:
        pid = item.get("product_id", "")
        stores = store_map.get(pid)
        base_title  = item.get("title", "Unknown")
        base_rating = item.get("rating")
        base_reviews = item.get("reviews")
        thumbnail = _thumbnail(item)

        if stores:
            for store in stores[:3]:
                url = store["link"]
                try:
                    domain = urlparse(url).netloc.replace("www.", "")
                except Exception:
                    domain = None
                raw_price = (store.get("extracted_price") or store.get("price")
                             or item.get("extracted_price") or item.get("price", 0))
                try:
                    listings.append(Listing(
                        title=base_title,
                        price=_parse_price(raw_price),
                        merchant=store["name"],
                        domain=domain,
                        rating=base_rating,
                        reviews=base_reviews,
                        url=url,
                        thumbnail=thumbnail,
                    ).model_dump())
                except Exception:
                    continue
        else:
            # Fallback: test fixture with a plain link, or product API was not called
            # for this item (it didn't make the top-10 cut).
            link = item.get("link", item.get("product_link", ""))
            if not link or "google.com" in link:
                continue          # skip bare Google Shopping URLs — Firecrawl can't use them
            try:
                domain = urlparse(link).netloc.replace("www.", "") or None
            except Exception:
                domain = None
            try:
                listings.append(Listing(
                    title=base_title,
                    price=_parse_price(item.get("extracted_price") or item.get("price", 0)),
                    merchant=item.get("source", item.get("merchant", "Unknown")),
                    domain=domain,
                    rating=base_rating,
                    reviews=base_reviews,
                    url=link,
                    thumbnail=thumbnail,
                ).model_dump())
            except Exception:
                continue

    return listings


@tool
def search_listings(query: str, max_results: int = 20) -> list:
    """Search online stores for clothing listings using Google Shopping.

    Args:
        query: What to search for, for example "black straight jeans under $80".
        max_results: Maximum number of results to return (default 20).

    Returns:
        A list of listings with title, price, merchant, domain, rating, reviews and url.
        Returns an empty list if the search fails.
    """
    if search_snapshot.replay_on():
        saved = search_snapshot.load(query, max_results)
        if saved is None:
            return [{"error": "No saved search for this query. Run it once without --frozen first.", "available": False}]
        return saved

    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        return [{"error": "SERPAPI_KEY not configured", "available": False}]

    params = {
        "engine": "google_shopping",
        "q": query,
        "api_key": api_key,
        # Fetch a wider pool so the scorer has enough candidates to pick from.
        # This is 1 API call regardless of num — the savings come from limiting
        # the follow-on product API calls to _PRODUCT_API_LIMIT.
        "num": str(min(max_results * 2, 40)),
        "gl": "us",
        "hl": "en",
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(SERPAPI_BASE, params=params)
            response.raise_for_status()
            data = response.json()

        if "error" in data:
            return [{"error": data["error"], "available": False}]

        listings = _extract_listings(data, api_key)
        listings = listings[:max_results]

        if not listings:
            return [{"error": "No listings found for this query", "available": False}]

        try:
            search_snapshot.save(query, max_results, listings)
        except OSError:
            pass
        return listings

    except httpx.TimeoutException:
        return [{"error": "Search timed out", "available": False}]
    except httpx.HTTPStatusError as e:
        return [{"error": f"HTTP error: {e.response.status_code}", "available": False}]
    except Exception as e:
        return [{"error": str(e), "available": False}]
