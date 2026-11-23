# Product photo: og:image first, extractor URL only when the page really contains it, never guessed.
import pytest
from helpers import load_fixture

from quickshop.evidence.firecrawl_client import FirecrawlClient
from quickshop.evidence.page_fields import clean_image_url
from quickshop.evidence.service import build_record
from quickshop.evidence.firecrawl_client import RawExtraction

PAGE = "https://shop.test/p/1"
OG = "https://cdn.shop.test/img/main.jpg"
IN_PAGE = "https://cdn.shop.test/img/other.jpg"


def _raw(*, og=None, extractor=None, markdown="# Tee\n\n![Tee](" + IN_PAGE + ")\n"):
    d = load_fixture("blend_tee")
    fields = dict(d["json"], image_url=extractor)
    return RawExtraction(PAGE, True, None, markdown, fields, 200, 5, og_image=og)


def test_og_image_is_preferred():
    assert build_record(PAGE, PAGE, _raw(og=OG, extractor=IN_PAGE)).image_url == OG


def test_extractor_url_is_used_when_the_page_contains_it():
    assert build_record(PAGE, PAGE, _raw(extractor=IN_PAGE)).image_url == IN_PAGE


def test_extractor_url_not_on_the_page_is_discarded():
    r = build_record(PAGE, PAGE, _raw(extractor="https://cdn.shop.test/img/invented.jpg"))
    assert r.image_url is None
    assert any("image url discarded" in n for n in r.parse_notes)


def test_no_image_anywhere_is_none():
    assert build_record(PAGE, PAGE, _raw()).image_url is None


def test_relative_og_image_is_made_absolute():
    assert build_record(PAGE, PAGE, _raw(og="/img/main.jpg")).image_url == "https://shop.test/img/main.jpg"


@pytest.mark.parametrize("bad", ["data:image/png;base64,AAAA", "javascript:alert(1)", "ftp://x/y.png", "not a url", "", None, "https://a b/c.png"])
def test_unsafe_or_invalid_image_values_are_rejected(bad):
    assert clean_image_url(bad) is None
    assert build_record(PAGE, PAGE, _raw(og=bad)).image_url is None


def test_protocol_relative_url_gets_https():
    assert clean_image_url("//cdn.shop.test/a.jpg") == "https://cdn.shop.test/a.jpg"


def test_existing_fixtures_without_an_image_still_parse():
    d = load_fixture("blend_tee")
    r = build_record(PAGE, PAGE, RawExtraction(PAGE, True, None, d["markdown"], d["json"], 200, 5))
    assert r.image_url is None and r.status == "ok"


def test_client_reads_og_image_from_metadata():
    class Meta:
        status_code, credits_used, og_image = 200, 5, OG

    class Doc:
        metadata, markdown = Meta(), "# Tee\n"
        json = {"is_product_page": True, "title": "Tee", "price_amount": 9.0}

    class Scraper:
        def scrape(self, url, *, formats, timeout):
            return Doc()

    raw = FirecrawlClient("key", scraper=Scraper()).scrape_product(PAGE)
    assert raw.ok and raw.og_image == OG
