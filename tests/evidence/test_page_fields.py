import pytest

from quickshop.evidence import page_fields as pf


@pytest.mark.parametrize("text,expected", [
    ("In stock", True), ("Hurry! Only 2 left!", True), ("Low stock", True), ("Add to cart", True),
    ("Out of Stock", False), ("Sold out", False), ("We're sorry but this product is no longer available online.", False),
    ("Currently unavailable", False),
    ("Color:red-Out of stock Clothing Size:M-Out of stock", False),
    ("Size S: In stock. Size M: Out of stock", None),     # contradictory: do not guess
    ("Free shipping on orders over $50", None), ("", None), (None, None),
])
def test_stock_from_text(text, expected):
    assert pf.stock_from_text(text) is expected


@pytest.mark.parametrize("text,expected", [
    ("Made in Portugal", "Portugal"), ("Country of origin: Vietnam", "Vietnam"), ("Italy", "Italy"),
    ("Product of Türkiye.", "Türkiye"), ("Imported", None), ("", None), (None, None),
])
def test_parse_origin(text, expected):
    assert pf.parse_origin(text) == expected


@pytest.mark.parametrize("code,text,expected", [
    ("usd", None, "USD"), (None, "£19.99", "GBP"), ("€", None, "EUR"), (None, "19.99", None), ("DOLLARS", None, None)])
def test_currency(code, text, expected):
    assert pf.normalize_currency(code, text) == expected


def test_appears_verbatim_ignores_markdown_decoration():
    assert pf.appears_verbatim("60% Cotton, 40% Polyester", "| **Material** | 60% Cotton,  40% Polyester |")
    assert not pf.appears_verbatim("100% Cotton", "no fabric info here")


def test_appears_verbatim_ignores_list_bullets():
    page = "**Materials**\n\n• Shell: 100% Cotton\n\n• Lining: 100% Polyester\n\n- Care: machine wash"
    assert pf.appears_verbatim("Shell: 100% Cotton\nLining: 100% Polyester", page)      # extractor dropped the bullets
    assert pf.appears_verbatim("• Shell: 100% Cotton\n• Lining: 100% Polyester", page)
    assert not pf.appears_verbatim("Shell: 90% Cotton\nLining: 100% Polyester", page)    # a changed number still fails


@pytest.mark.parametrize("code,text,expected", [
    ("USD", "C$169.39", "CAD"), ("$", "CA$20", "CAD"), ("USD", "A$30.00", "AUD"), ("USD", "NZ$15", "NZD"),
    ("USD", "$24.00", "USD"), ("USD", "US$24.00", "USD"), (None, "C$5", "CAD"), ("EUR", "€89,90", "EUR"),
    ("GBP", "£19.99", "GBP"), ("USD", None, "USD")])
def test_explicit_price_prefix_beats_extractor_currency(code, text, expected):
    assert pf.normalize_currency(code, text) == expected
