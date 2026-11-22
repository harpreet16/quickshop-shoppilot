# Encoding repair: the Gap Factory failure from Milestone 2 (double-encoded dashes).
from quickshop.evidence.text_fix import _cp1252_roundtrip, looks_garbled, repair_text

GARBLED = "Ã¢â‚¬â€œ Ã¢â‚¬â€œ cotton blend"


def test_clean_text_is_unchanged():
    assert repair_text("79% Cotton – 21% Polyester") == "79% Cotton – 21% Polyester"
    assert repair_text(None) is None and repair_text("") == ""


def test_double_encoded_text_is_repaired():
    fixed = repair_text(GARBLED)
    assert "–" in fixed and "cotton blend" in fixed and not looks_garbled(fixed)


def test_fallback_handles_what_plain_latin1_cannot():
    # the proposed encode('latin-1') fallback raises on this string; the cp1252 loop does not
    try:
        GARBLED.encode("latin-1")
        raised = False
    except UnicodeEncodeError:
        raised = True
    assert raised
    assert "–" in _cp1252_roundtrip(GARBLED)


def test_single_encoding_is_repaired():
    assert repair_text("CafÃ© cotton") == "Café cotton"


def test_unrepairable_text_is_returned_not_raised():
    assert isinstance(repair_text("Ã garbage \x81 only"), str)
