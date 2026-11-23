# Fabric stated in a retailer's own schema.org Product data is a last-resort source for composition.
# It is used only when the extractor and the page text both found nothing, and never when ambiguous.
import json

from helpers import FakeScraper, load_fixture

from quickshop.evidence.firecrawl_client import FirecrawlClient, RawExtraction
from quickshop.evidence.page_fields import material_from_jsonld
from quickshop.evidence.service import build_record

PAGE = "https://shop.test/p/1"
AE_MATERIAL = "78% Cotton, 21% Recycled Cotton, 1% Elastane"


def ld(*documents) -> str:
    scripts = "".join(f'<script type="application/ld+json">{json.dumps(d)}</script>' for d in documents)
    return f"<html><head>{scripts}</head><body>page</body></html>"


def product(material=None, **extra):
    node = {"@context": "https://schema.org", "@type": "Product", "name": "Jean", **extra}
    if material is not None:
        node["material"] = material
    return node


def test_reads_the_material_of_a_product_node():
    assert material_from_jsonld(ld(product(AE_MATERIAL))) == AE_MATERIAL


def test_product_subtypes_and_type_lists_count():
    html = ld({"@type": ["IndividualProduct", "Thing"], "material": AE_MATERIAL})
    assert material_from_jsonld(html) == AE_MATERIAL


def test_graph_documents_are_read():
    html = ld({"@context": "https://schema.org", "@graph": [{"@type": "WebSite"}, product(AE_MATERIAL)]})
    assert material_from_jsonld(html) == AE_MATERIAL


def test_a_list_of_materials_is_joined():
    assert material_from_jsonld(ld(product(["99% Cotton", "1% Elastane"]))) == "99% Cotton, 1% Elastane"


def test_the_same_material_repeated_is_still_one_answer():
    assert material_from_jsonld(ld(product(AE_MATERIAL), product("  78% cotton, 21% recycled cotton, 1% elastane "))) == AE_MATERIAL


def test_two_different_materials_are_ambiguous_so_none():
    assert material_from_jsonld(ld(product("100% Cotton"), product("100% Polyester"))) is None


def test_nested_related_products_are_ignored():
    related = product("100% Polyester")
    html = ld(product(AE_MATERIAL, isRelatedTo=[related], isSimilarTo=related))
    assert material_from_jsonld(html) == AE_MATERIAL


def test_non_product_nodes_are_ignored():
    assert material_from_jsonld(ld({"@type": "Organization", "material": "100% Cotton"})) is None


def test_missing_empty_or_broken_data_gives_none():
    assert material_from_jsonld(None) is None
    assert material_from_jsonld("") is None
    assert material_from_jsonld("<html>no structured data</html>") is None
    assert material_from_jsonld(ld(product())) is None
    assert material_from_jsonld(ld(product("   "))) is None
    assert material_from_jsonld('<script type="application/ld+json">{not json</script>') is None


def _raw(*, material, markdown="# Jean\n\nA slim straight jean.\n", composition_text=None):
    fields = {"is_product_page": True, "title": "Jean", "composition_text": composition_text}
    return RawExtraction(PAGE, True, None, markdown, fields, 200, 5, structured_material=material)


def test_structured_material_fills_in_when_nothing_else_found_it():
    record = build_record(PAGE, PAGE, _raw(material=AE_MATERIAL))
    assert record.composition_raw == AE_MATERIAL
    assert record.natural_fiber_pct is not None
    assert any("structured product data" in n for n in record.parse_notes)


def test_without_structured_material_composition_stays_unknown():
    record = build_record(PAGE, PAGE, _raw(material=None))
    assert record.composition_raw is None and record.natural_fiber_pct is None


def test_the_pages_own_text_wins_over_structured_data():
    markdown = "# Jean\n\nFabric: 100% Cotton\n"
    record = build_record(PAGE, PAGE, _raw(material=AE_MATERIAL, markdown=markdown))
    assert "100% Cotton" in record.composition_raw
    assert not any("structured product data" in n for n in record.parse_notes)


def test_the_extractors_composition_wins_over_structured_data():
    markdown = "# Jean\n\nMade of 60% Cotton, 40% Polyester\n"
    record = build_record(PAGE, PAGE, _raw(material=AE_MATERIAL, markdown=markdown, composition_text="60% Cotton, 40% Polyester"))
    assert record.composition_raw == "60% Cotton, 40% Polyester"


def test_the_client_requests_raw_html_and_extracts_the_material():
    doc = load_fixture("blend_tee")
    del doc["json"]["composition_text"]
    doc["markdown"] = "# Everyday Crew\n\nA soft tee.\n"
    doc["rawHtml"] = ld(product(AE_MATERIAL))
    scraper = FakeScraper(doc)
    raw = FirecrawlClient(scraper=scraper, sleep=lambda s: None).scrape_product(PAGE)
    assert "rawHtml" in scraper.calls[0]["formats"]
    assert raw.structured_material == AE_MATERIAL


def test_the_client_copes_with_a_scrape_that_has_no_html():
    c = FirecrawlClient(scraper=FakeScraper(load_fixture("blend_tee")), sleep=lambda s: None)
    assert c.scrape_product(PAGE).structured_material is None
