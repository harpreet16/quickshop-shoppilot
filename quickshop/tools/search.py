# search_listings using SerpAPI Google Shopping
import os
from typing import Optional

from dotenv import load_dotenv
from strands import tool
import httpx

from quickshop.schemas import Listing

load_dotenv()

SERPAPI_BASE = "https://serpapi.com/search"


def _extract_listings(results: dict) -> list[dict]:
    """Extract listings from SerpAPI shopping results."""
    listings = []

    shopping_results = results.get("shopping_results", [])

    for item in shopping_results:
        try:
            price_str = item.get("extracted_price") or item.get("price", "0")
            if isinstance(price_str, str):
                price_str = price_str.replace("$", "").replace(",", "").strip()
                try:
                    price = float(price_str)
                except ValueError:
                    price = 0.0
            else:
                price = float(price_str) if price_str else 0.0

            merchant = item.get("source", item.get("merchant", "Unknown"))

            link = item.get("link", item.get("product_link", ""))
            domain = None
            if link:
                try:
                    from urllib.parse import urlparse

                    parsed = urlparse(link)
                    domain = parsed.netloc.replace("www.", "")
                except Exception:
                    pass

            listing = Listing(
                title=item.get("title", "Unknown"),
                price=price,
                merchant=merchant,
                domain=domain,
                rating=item.get("rating"),
                reviews=item.get("reviews"),
                url=link,
            )
            listings.append(listing.model_dump())
        except Exception as e:
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
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        return [{"error": "SERPAPI_KEY not configured", "available": False}]

    params = {
        "engine": "google_shopping",
        "q": query,
        "api_key": api_key,
        "num": str(min(max_results, 100)),
        "gl": "us",
        "hl": "en",
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(SERPAPI_BASE, params=params)
            response.raise_for_status()
            data = response.json()

        listings = _extract_listings(data)

        if not listings:
            if "error" in data:
                return [{"error": data["error"], "available": False}]
            return []

        return listings[:max_results]

    except httpx.TimeoutException:
        return [{"error": "Search timed out", "available": False}]
    except httpx.HTTPStatusError as e:
        return [{"error": f"HTTP error: {e.response.status_code}", "available": False}]
    except Exception as e:
        return [{"error": str(e), "available": False}]
