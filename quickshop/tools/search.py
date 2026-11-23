# search_listings using SerpAPI Google Shopping
# Each shopping_results item only gives a google.com/search?ibp=oshop URL — not a real product
# page. We call serpapi_product_api (in parallel) for each result to get the actual retailer
# URLs from the "stores" list, so Firecrawl can scrape them.
import os
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
# How many product-API calls to fire in parallel. Kept low to be a good API citizen.
_PRODUCT_API_WORKERS = 5


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


def _fetch_stores(product_api_url: str, api_key: str) -> list[dict]:
    """Call serpapi_product_api and return stores that have a real http(s) URL.

    The api_key must be appended directly to the URL string — the endpoint
    has an existing query string and httpx params= does not merge into it
    correctly for the google_product engine.
    """
    try:
        full_url = f"{product_api_url}&api_key={api_key}"
        with httpx.Client(timeout=15.0) as client:
            r = client.get(full_url)
            r.raise_for_status()
            data = r.json()
        stores = data.get("product_results", {}).get("stores", [])
        # Only keep stores whose link is an absolute URL — relative /goto?url= links are unusable
        return [s for s in stores if isinstance(s.get("link"), str) and s["link"].startswith("http")]
    except Exception:
        return []


def _extract_listings(results: dict, api_key: str = "") -> list[dict]:
    """
    Build Listing objects from SerpAPI shopping_results.

    For each result we call serpapi_product_api (in parallel) to get the real
    retailer URLs.  One Listing is created per real store (up to 3 per product),
    so the agent sees e.g. Walmart/$19.98, Wrangler/$27.99, and Target/$22.00
    as separate candidates rather than a single google.com URL it cannot read.

    Fallback: if serpapi_product_api is absent (e.g. test fixtures), the item's
    own link field is used directly — so offline tests keep working unchanged.
    """
    shopping_results = results.get("shopping_results", [])
    if not shopping_results:
        return []

    # --- parallel product-API calls for items that have the endpoint ---
    store_map: dict[str, list[dict]] = {}
    items_with_api = [(item, item["serpapi_product_api"])
                      for item in shopping_results
                      if item.get("serpapi_product_api")]

    if items_with_api and api_key:
        with ThreadPoolExecutor(max_workers=_PRODUCT_API_WORKERS) as pool:
            future_to_id = {
                pool.submit(_fetch_stores, url, api_key): item.get("product_id", str(i))
                for i, (item, url) in enumerate(items_with_api)
            }
            for future in as_completed(future_to_id):
                pid = future_to_id[future]
                try:
                    store_map[pid] = future.result()
                except Exception:
                    store_map[pid] = []

    # --- build listings ---
    listings: list[dict] = []
    for item in shopping_results:
        pid = item.get("product_id", "")
        stores = store_map.get(pid)
        base_title = item.get("title", "Unknown")
        base_rating = item.get("rating")
        base_reviews = item.get("reviews")
        thumbnail = _thumbnail(item)

        if stores:
            # Create one listing per real retailer (capped at 3 per product)
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
            # No product API available (test fixture) or all stores had relative URLs.
            # Fall back to the item's own link so offline tests stay green.
            link = item.get("link", item.get("product_link", ""))
            if not link:
                continue
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
    # Frozen mode: use only saved searches, never call SerpAPI
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
        # Fetch more than max_results at the top level because some items may have
        # no real retailer URL and will be dropped.
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

        # Save so a later --frozen run gets exactly these listings
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
