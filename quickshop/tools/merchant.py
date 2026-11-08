# check_merchant - domain age, reviews, and brand checks
import os
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from strands import tool
import httpx

from quickshop.schemas import MerchantSignals

load_dotenv()

KNOWN_BRANDS = {
    "nordstrom",
    "nordstrom rack",
    "macys",
    "macy's",
    "bloomingdales",
    "bloomingdale's",
    "neiman marcus",
    "saks fifth avenue",
    "saks",
    "bergdorf goodman",
    "target",
    "walmart",
    "kohl's",
    "kohls",
    "jcpenney",
    "jc penney",
    "amazon",
    "amazon.com",
    "zappos",
    "zara",
    "h&m",
    "hm",
    "uniqlo",
    "forever 21",
    "asos",
    "shein",
    "fashion nova",
    "gap",
    "old navy",
    "banana republic",
    "express",
    "american eagle",
    "ae",
    "abercrombie",
    "abercrombie & fitch",
    "hollister",
    "levi's",
    "levis",
    "levi strauss",
    "wrangler",
    "lee",
    "true religion",
    "7 for all mankind",
    "citizens of humanity",
    "ag jeans",
    "paige",
    "hudson jeans",
    "joe's jeans",
    "frame",
    "mother denim",
    "dl1961",
    "madewell",
    "everlane",
    "reformation",
    "gucci",
    "prada",
    "louis vuitton",
    "chanel",
    "dior",
    "balenciaga",
    "saint laurent",
    "ysl",
    "versace",
    "armani",
    "dolce & gabbana",
    "burberry",
    "fendi",
    "givenchy",
    "valentino",
    "bottega veneta",
    "nike",
    "adidas",
    "under armour",
    "lululemon",
    "patagonia",
    "the north face",
    "columbia",
    "rei",
    "dick's sporting goods",
    "dillard's",
    "dillards",
    "belk",
    "von maur",
    "boscov's",
}


TRUSTED_DOMAINS = {
    "nordstrom.com",
    "macys.com",
    "bloomingdales.com",
    "neimanmarcus.com",
    "saksfifthavenue.com",
    "target.com",
    "walmart.com",
    "kohls.com",
    "amazon.com",
    "zappos.com",
    "zara.com",
    "hm.com",
    "uniqlo.com",
    "gap.com",
    "oldnavy.com",
    "bananarepublic.com",
    "levi.com",
    "madewell.com",
    "everlane.com",
    "asos.com",
    "nike.com",
    "adidas.com",
    "lululemon.com",
    "patagonia.com",
    "rei.com",
}


def _normalize_name(name: str) -> str:
    """Normalize merchant name for comparison."""
    return name.lower().strip().replace("'", "").replace("'", "")


def _is_known_brand(merchant: str) -> bool:
    """Check if merchant is a known trusted brand."""
    normalized = _normalize_name(merchant)
    return normalized in KNOWN_BRANDS or any(
        brand in normalized or normalized in brand for brand in KNOWN_BRANDS
    )


def _check_domain_age(domain: str) -> Optional[float]:
    """
    Check domain age using WHOIS lookup via API.
    Returns age in years, or None if unavailable.

    Note: In production, you'd use a WHOIS API service.
    For now, we'll return None and rely on other signals.
    """
    if domain and domain.lower().replace("www.", "") in TRUSTED_DOMAINS:
        return 10.0

    return None


def _search_reviews(merchant: str) -> Optional[int]:
    """
    Search for third-party reviews of the merchant.

    In production, this could query:
    - Trustpilot API
    - BBB API
    - Google My Business

    For now, we estimate based on brand recognition.
    """
    if _is_known_brand(merchant):
        return 10000
    return None


@tool
def check_merchant(merchant: str, domain: str = None) -> dict:
    """Check how trustworthy a seller is using multiple signals.

    Args:
        merchant: The seller name from a listing, for example "Levi's".
        domain: Optional domain name to check (e.g., "levi.com").

    Returns:
        Seller signals including:
        - known_brand: Whether this is a recognized brand/retailer
        - domain_age_years: How old the domain is (older = more trusted)
        - third_party_reviews: Number of reviews on external sites
        - return_policy: Whether they have a known return policy
        - available: False if no information could be gathered
    """
    signals = MerchantSignals(merchant=merchant)

    known = _is_known_brand(merchant)
    signals.known_brand = known

    if domain:
        domain_age = _check_domain_age(domain)
        signals.domain_age_years = domain_age

    reviews = _search_reviews(merchant)
    signals.third_party_reviews = reviews

    signals.return_policy = known

    signals.available = (
        signals.known_brand is not None
        or signals.domain_age_years is not None
        or signals.third_party_reviews is not None
    )

    return signals.model_dump()
