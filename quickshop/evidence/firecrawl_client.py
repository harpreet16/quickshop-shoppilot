# Thin wrapper around Firecrawl. scrape_product() never raises: every failure becomes a RawExtraction
# with ok=False and a reason string. The real SDK sits behind a one-method interface so tests inject a fake.
from __future__ import annotations

import os
import re
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol

from dotenv import load_dotenv
from quickshop.evidence.page_fields import material_from_jsonld

load_dotenv()   # makes FIRECRAWL_API_KEY available even if nothing else loaded .env first

# Cost of one scrape with JSON extraction (1 base + 4 for JSON mode), used only when the API
# does not report credits_used itself.
ESTIMATED_CREDITS_PER_SCRAPE = 5
DEFAULT_TIMEOUT_MS = 60_000     # Firecrawl's scrape timeout is in milliseconds

# The agent can ask for several page reads at once, and Firecrawl answers a burst with HTTP 429.
# At most this many scrapes run at the same time in this process (the rest wait their turn).
MAX_CONCURRENT_SCRAPES = max(1, int(os.getenv("QUICKSHOP_FIRECRAWL_CONCURRENCY") or 2))
_SCRAPE_SLOTS = threading.BoundedSemaphore(MAX_CONCURRENT_SCRAPES)
RATE_LIMIT_BACKOFF_FACTOR = 4   # after a 429, wait this many times longer than for other errors

EXTRACTION_PROMPT = (
    "Extract facts about the single clothing product this page is about. "
    "Copy composition, origin, return policy, price, rating and availability text VERBATIM from the page; "
    "do not paraphrase, summarise, translate or correct it. "
    "If a field is not on the page, return null. Never guess. "
    "If the page is not a product page for one clothing item, set is_product_page to false."
)

_S = {"type": ["string", "null"]}
RAW_EXTRACTION_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "is_product_page": {"type": ["boolean", "null"]},
        "title": _S, "brand": _S, "seller_name": _S,
        "price_amount": {"type": ["number", "null"]},
        "price_currency": _S,
        "price_text": {**_S, "description": "the price exactly as shown, e.g. '$29.99'"},
        "composition_text": {**_S, "description": "the fabric/material composition exactly as written, "
                                                   "including part labels such as Shell/Lining"},
        "care_text": _S,
        "origin_text": {**_S, "description": "the made-in / country-of-origin text exactly as written"},
        "return_policy_text": {**_S, "description": "the return policy text exactly as written"},
        "rating": {"type": ["number", "null"]},
        "review_count": {"type": ["integer", "null"]},
        "rating_text": _S,
        "in_stock": {"type": ["boolean", "null"]},
        "availability_text": _S,
        "image_url": {**_S, "description": "the full https URL of the MAIN product photo exactly as it appears "
                                           "on the page; not a colour swatch, logo, icon or another product"},
    },
}

_SETUP_ERRORS = ("FIRECRAWL_API_KEY is not set", "rejected the API key", "credits exhausted")

_BLOCK_PATTERNS = re.compile(
    r"captcha|access denied|are you a (?:robot|human)|verify you are (?:a )?human|"
    r"unusual traffic|request blocked|enable javascript and cookies|attention required",
    re.IGNORECASE,
)


@dataclass
class RawExtraction:
    url: str
    ok: bool
    error_reason: str | None = None
    markdown: str | None = None
    fields: dict = field(default_factory=dict)
    http_status: int | None = None
    credits_used: int = 0
    extraction_error: str | None = None    # set when the JSON extraction was unusable but markdown exists
    og_image: str | None = None            # page's og:image from Firecrawl metadata: the preferred product photo
    structured_material: str | None = None  # fabric from the page's own schema.org product data, when it states exactly one
    cacheable: bool = True                 # False for setup problems (no/bad key, no credits) so they are never remembered


class Scraper(Protocol):
    def scrape(self, url: str, *, formats: list, timeout: int) -> Any: ...


class UsageCounter:
    """Calls and credits spent. Part A's budget logic reads this; nothing here enforces a limit."""

    def __init__(self):
        self._lock = threading.Lock()
        self.calls = self.successes = self.failures = self.retries = self.credits_used = 0

    def add(self, **kw):
        with self._lock:
            for k, v in kw.items():
                setattr(self, k, getattr(self, k) + v)

    def snapshot(self) -> dict:
        with self._lock:
            return {"calls": self.calls, "successes": self.successes, "failures": self.failures,
                    "retries": self.retries, "credits_used": self.credits_used}


class _SdkScraper:
    def __init__(self, api_key: str):
        from firecrawl import Firecrawl
        self._client = Firecrawl(api_key=api_key)

    def scrape(self, url, *, formats, timeout):
        return self._client.scrape(url, formats=formats, timeout=timeout)


def _attr(obj, *names):
    """Read a field from an SDK object or a plain dict, trying several spellings."""
    if obj is None:
        return None
    for n in names:
        v = obj.get(n) if isinstance(obj, dict) else getattr(obj, n, None)
        if v is not None:
            return v
    return None


def _classify_error(exc: Exception) -> tuple[bool, str]:
    """(retryable, reason) for an exception raised by the scraper."""
    status = getattr(exc, "status_code", None)
    name = type(exc).__name__
    msg = str(exc)[:200]
    if isinstance(exc, TimeoutError) or "Timeout" in name or status == 408:
        return True, "timeout"
    if status == 429 or name == "RateLimitError":
        return True, "rate limited by Firecrawl (HTTP 429)"
    if status in (500, 502, 503, 504) or name == "InternalServerError":
        return True, f"Firecrawl server error (HTTP {status or 500})"
    if "Connection" in name:
        return True, "network error"
    if status == 402 or name == "PaymentRequiredError":
        return False, "Firecrawl credits exhausted (HTTP 402)"
    if status == 401 or name == "UnauthorizedError":
        return False, "Firecrawl rejected the API key (HTTP 401)"
    if status == 403:
        return False, "site blocked or unsupported (HTTP 403)"
    if status == 404:
        return False, "page not found (HTTP 404)"
    return False, f"scrape failed: {name}: {msg}"


class FirecrawlClient:
    def __init__(self, api_key: str | None = None, *, scraper: Scraper | None = None,
                 timeout_ms: int = DEFAULT_TIMEOUT_MS, max_retries: int = 3, backoff_s: float = 1.0,
                 sleep: Callable[[float], None] = time.sleep):
        self.api_key = api_key if api_key is not None else os.getenv("FIRECRAWL_API_KEY")
        self._scraper = scraper
        self.timeout_ms = timeout_ms
        self.max_retries = max_retries
        self.backoff_s = backoff_s
        self._sleep = sleep
        self.usage = UsageCounter()

    # -- public
    def scrape_product(self, url: str) -> RawExtraction:
        try:
            return self._scrape(url)
        except Exception as exc:  # last-resort guard: this function must never raise
            self.usage.add(failures=1)
            return RawExtraction(url, False, f"unexpected error: {type(exc).__name__}: {str(exc)[:200]}")

    # -- internals
    def _get_scraper(self) -> Scraper | None:
        if self._scraper is None and self.api_key:
            self._scraper = _SdkScraper(self.api_key)
        return self._scraper

    def _fail(self, url, reason, **kw) -> RawExtraction:
        self.usage.add(failures=1)
        kw.setdefault("cacheable", not any(m in reason for m in _SETUP_ERRORS))
        return RawExtraction(url, False, reason, **kw)

    def _scrape(self, url: str) -> RawExtraction:
        scraper = self._get_scraper()
        if scraper is None:
            return self._fail(url, "FIRECRAWL_API_KEY is not set")
        formats = ["markdown", {"type": "json", "schema": RAW_EXTRACTION_SCHEMA, "prompt": EXTRACTION_PROMPT}, "rawHtml"]

        doc, reason = None, "scrape failed"
        for attempt in range(self.max_retries + 1):
            self.usage.add(calls=1)
            try:
                with _SCRAPE_SLOTS:
                    doc = scraper.scrape(url, formats=formats, timeout=self.timeout_ms)
                break
            except Exception as exc:
                retryable, reason = _classify_error(exc)
                if not retryable or attempt == self.max_retries:
                    return self._fail(url, reason if not retryable else f"{reason} after {attempt + 1} tries")
                self.usage.add(retries=1)
                wait = self.backoff_s * (2 ** attempt)
                if "429" in reason:
                    wait *= RATE_LIMIT_BACKOFF_FACTOR      # being rate limited needs a real pause, not 1 second
                self._sleep(wait)

        meta = _attr(doc, "metadata")
        markdown = _attr(doc, "markdown")
        fields = _attr(doc, "json")
        status = _attr(meta, "status_code", "statusCode")
        credits = _attr(meta, "credits_used", "creditsUsed")
        credits = int(credits) if isinstance(credits, (int, float)) else ESTIMATED_CREDITS_PER_SCRAPE
        self.usage.add(credits_used=credits)

        if isinstance(status, int) and status >= 400:
            hint = " (blocked)" if status in (401, 403, 429) else ""
            return self._fail(url, f"page returned HTTP {status}{hint}", http_status=status, credits_used=credits)
        has_md = isinstance(markdown, str) and bool(markdown.strip())
        has_fields = isinstance(fields, dict) and any(v not in (None, "", []) for v in fields.values())
        if not has_md and not has_fields:
            return self._fail(url, "empty page: no content returned", http_status=status, credits_used=credits)
        if has_md and not has_fields and len(markdown) < 1500 and _BLOCK_PATTERNS.search(markdown):
            return self._fail(url, "blocked by bot protection or captcha", http_status=status,
                              markdown=markdown, credits_used=credits)

        extraction_error = None
        if not isinstance(fields, dict):
            extraction_error = "extraction JSON missing or malformed"
            fields = {}
        elif fields.get("is_product_page") is False:
            return self._fail(url, "not a product page", http_status=status, markdown=markdown,
                              credits_used=credits)
        product_keys = ("title", "price_amount", "price_text", "composition_text")
        if fields and fields.get("is_product_page") is not True and not any(fields.get(k) for k in product_keys):
            return self._fail(url, "not a product page: no product data found", http_status=status,
                              markdown=markdown, credits_used=credits)

        og_image = _attr(meta, "og_image", "ogImage")
        og_image = og_image.strip() if isinstance(og_image, str) and og_image.strip() else None

        self.usage.add(successes=1)
        return RawExtraction(url, True, None, markdown if has_md else None, fields, status, credits,
                             extraction_error, og_image=og_image,
                             structured_material=material_from_jsonld(_attr(doc, "raw_html", "rawHtml")))
