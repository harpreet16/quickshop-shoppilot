# Small deterministic helpers that clean the non-composition fields the extractor returns.
# Each returns None (never a guess) when the value cannot be read safely.
from __future__ import annotations

import json
import re

_CURRENCY_SYMBOLS = {"$": "USD", "£": "GBP", "€": "EUR"}
_ORIGIN_PATTERNS = [
    re.compile(r"(?:made|manufactured|produced|assembled)\s+in\s+(?P<c>[^\n,.;()|]+)", re.I),
    re.compile(r"country\s+of\s+(?:origin|manufacture)\s*[:\-]?\s*(?P<c>[^\n,.;()|]+)", re.I),
    re.compile(r"product\s+of\s+(?P<c>[^\n,.;()|]+)", re.I),
    re.compile(r"imported\s+from\s+(?P<c>[^\n,.;()|]+)", re.I),
]


def clean_text(value) -> str | None:
    if value is None:
        return None
    s = re.sub(r"\s+", " ", str(value)).strip()
    return s or None


def to_float(value) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    m = re.search(r"\d+(?:[.,]\d+)?", str(value).replace(" ", ""))
    return float(m.group().replace(",", ".")) if m else None


def to_int(value) -> int | None:
    f = to_float(value)
    if f is None or f < 0:
        return None
    return int(round(f))


def to_bool(value) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        v = value.strip().lower()
        if v in {"true", "yes", "in stock", "available"}:
            return True
        if v in {"false", "no", "out of stock", "sold out", "unavailable"}:
            return False
    return None


_OUT_RE = re.compile(r"out of stock|sold out|no longer available|currently unavailable|unavailable|not available|"
                     r"discontinued|notify me when|back in stock soon", re.I)
_IN_RE = re.compile(r"\bin stock\b|only \d+ left|\d+ left in stock|low stock|few left|ready to ship|"
                    r"add to (?:cart|bag|basket)|available now", re.I)


def stock_from_text(text) -> bool | None:
    """Read stock from the page's own wording. None when absent or contradictory (e.g. per-variant text)."""
    t = clean_text(text)
    if not t:
        return None
    out, in_ = bool(_OUT_RE.search(t)), bool(_IN_RE.search(re.sub(_OUT_RE, " ", t)))
    if out == in_:
        return None
    return in_


_PREFIXED_DOLLARS = [(re.compile(r"(?<![A-Za-z])(?:CA|C)\$|\bCAD\b"), "CAD"),
                     (re.compile(r"(?<![A-Za-z])(?:AU|A)\$|\bAUD\b"), "AUD"),
                     (re.compile(r"(?<![A-Za-z])NZ\$|\bNZD\b"), "NZD"),
                     (re.compile(r"(?<![A-Za-z])US\$|\bUSD\b"), "USD")]


def normalize_currency(code, price_text=None) -> str | None:
    """Currency of the price. An explicit marker in the price text (C$, A$, US$ ...) beats the extractor's code,
    which sometimes says USD for a Canadian price. Else the 3-letter code; else a $, £ or € symbol; else None."""
    if isinstance(price_text, str):
        for pat, iso in _PREFIXED_DOLLARS:
            if pat.search(price_text):
                return iso
    if isinstance(code, str):
        c = code.strip()
        if c in _CURRENCY_SYMBOLS:
            return _CURRENCY_SYMBOLS[c]
        if len(c) == 3 and c.isalpha():
            return c.upper()
    if isinstance(price_text, str):
        for sym, iso in _CURRENCY_SYMBOLS.items():
            if sym in price_text:
                return iso
    return None


_NOT_A_COUNTRY = {"imported", "import", "domestic", "unknown", "n/a", "na", "none", "various", "multiple",
                  "see label", "see tag", "not specified", "other", "global", "worldwide"}


def parse_origin(text) -> str | None:
    """'Made in Portugal' -> 'Portugal'. A bare short country-like string is accepted as is."""
    t = clean_text(text)
    if not t:
        return None
    for pat in _ORIGIN_PATTERNS:
        m = pat.search(t)
        if m:
            country = m.group("c").strip(" .:-")
            return country if 2 <= len(country) <= 40 else None
    if t.strip(" .").lower() not in _NOT_A_COUNTRY and re.fullmatch(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ .'-]{1,38}", t):
        return t.strip(" .")
    return None


_BULLETS = "•●▪◦‣∙·"


def _squash(s: str) -> str:
    """Lowercase and drop whitespace, markdown decoration and list bullets, so layout differences never count as rewording."""
    s = re.sub(rf"[{_BULLETS}]", " ", s)
    s = re.sub(r"(?m)^\s*[-+]\s+", " ", s)       # "- item" / "+ item" list markers at line start
    return re.sub(r"[\s*_`|\\]+", " ", s).strip().lower()


def appears_verbatim(snippet: str | None, page_markdown: str | None) -> bool:
    """True if the snippet is really on the page (ignoring whitespace and markdown decoration)."""
    if not snippet or not page_markdown:
        return False
    return _squash(snippet) in _squash(page_markdown)


_JSONLD_BLOCK = re.compile(r"<script[^>]+application/ld\+json[^>]*>(.*?)</script>", re.S | re.I)
_PRODUCT_TYPES = {"product", "individualproduct", "productmodel", "productgroup"}


def _jsonld_nodes(data):
    """The top-level nodes of one JSON-LD document: a list, an object, or the items of an @graph."""
    if isinstance(data, list):
        for item in data:
            yield from _jsonld_nodes(item)
    elif isinstance(data, dict):
        if isinstance(data.get("@graph"), list):
            yield from _jsonld_nodes(data["@graph"])
        else:
            yield data


def _is_product_node(node: dict) -> bool:
    kind = node.get("@type")
    kinds = kind if isinstance(kind, list) else [kind]
    return any(isinstance(k, str) and k.lower() in _PRODUCT_TYPES for k in kinds)


def material_from_jsonld(html: str | None) -> str | None:
    """The fabric a retailer states in its own schema.org Product data, e.g. "78% Cotton, 1% Elastane".
    Only the page's top-level product entries count, never nested related products. If the page
    states more than one different material, that is ambiguous, so the answer is None, not a guess."""
    if not isinstance(html, str) or "ld+json" not in html.lower():
        return None
    found: dict[str, str] = {}
    for block in _JSONLD_BLOCK.findall(html):
        try:
            data = json.loads(block.strip())
        except ValueError:
            continue
        for node in _jsonld_nodes(data):
            if not _is_product_node(node):
                continue
            material = node.get("material")
            if isinstance(material, list):
                material = ", ".join(m for m in material if isinstance(m, str))
            if isinstance(material, str):
                text = " ".join(material.split())
                if text:
                    found.setdefault(text.lower(), text)
    return next(iter(found.values())) if len(found) == 1 else None


def clean_image_url(value, base_url: str | None = None) -> str | None:
    """An absolute http(s) image URL, or None. Rejects data:/javascript: URLs and anything not a URL."""
    from urllib.parse import urljoin, urlsplit

    text = clean_text(value)
    if not text or len(text) > 2000 or " " in text:
        return None
    if text.startswith("//"):
        text = "https:" + text
    elif base_url and not urlsplit(text).scheme:
        text = urljoin(base_url, text)
    parts = urlsplit(text)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        return None
    return text
