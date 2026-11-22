"""Synthetic pilot fixtures inspired by outputs/quickshop_output.txt, not live seller facts."""

from copy import deepcopy

from strands import tool

from quickshop.tools.scoring import score_product

PRODUCTS = [
    {
        "title": "Levi's Classic Straight Jeans — demo",
        "price": 48.65,
        "merchant": "Kohl's",
        "url": "https://example.com/demo/kohls-jeans",
        "domain": "kohls.com",
    },
    {
        "title": "Gap Straight Jeans — demo",
        "price": 29.99,
        "merchant": "Gap",
        "url": "https://example.com/demo/gap-jeans",
        "domain": "gap.com",
    },
    {
        "title": "Levi's Classic Straight Jeans — demo seller",
        "price": 34.99,
        "merchant": "eBay - authenticbargainsllc",
        "url": "https://example.com/demo/ebay-jeans",
        "domain": "ebay.com",
    },
]


def frozen_tools(ask_user):
    @tool
    def search_listings(query: str, max_results: int = 20) -> list:
        """Return fixed synthetic black-jeans demo listings, regardless of query."""
        return deepcopy(PRODUCTS[: max(0, min(max_results, 100))])

    @tool
    def check_merchant(merchant: str, domain: str | None = None) -> dict:
        """Return synthetic demo merchant signals, not verified live facts."""
        trusted = merchant in ("Kohl's", "Gap")
        return {
            "merchant": merchant,
            "known_brand": trusted,
            "domain_age_years": 10 if trusted else None,
            "third_party_reviews": 10000 if trusted else None,
            "return_policy": trusted,
            "available": True,
        }

    @tool
    def fetch_product_evidence(url: str) -> dict:
        """Return synthetic product evidence from the frozen pilot; never scrape."""
        product = next((p for p in PRODUCTS if p["url"] == url), None)
        if product is None:
            return {"url": url, "status": "unavailable", "error_reason": "Not in frozen demo"}
        known = product["merchant"] == "Kohl's"
        return {
            "url": url,
            "status": "ok" if known else "partial",
            "title": product["title"],
            "price": {"amount": product["price"], "currency": "USD"},
            "composition_raw": "79% cotton, 19% polyester, 2% elastane" if known else None,
            "natural_fiber_pct": 79 if known else None,
            "composition_confidence": "explicit" if known else "unknown",
            "parse_notes": ["Synthetic frozen demo evidence; not current product facts."],
        }

    return [search_listings, check_merchant, fetch_product_evidence, score_product, ask_user]
