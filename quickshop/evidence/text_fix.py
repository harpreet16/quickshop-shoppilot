# Repairs mojibake ("Ã¢â‚¬â€œ" where a dash should be) in page text before it is parsed.
# Some retailer pages (Gap Factory in the Milestone 2 run) come back double-encoded.
# Plain latin-1 re-decoding cannot fix that: the garbage contains cp1252 characters such as
# the euro sign that latin-1 cannot encode. So ftfy goes first and a cp1252 loop is the fallback.
from __future__ import annotations

try:  # ftfy is a declared dependency, but never let a missing install break page reading
    from ftfy import fix_text as _ftfy_fix
except ImportError:  # pragma: no cover
    _ftfy_fix = None

# characters that appear when UTF-8 bytes were read as cp1252/latin-1
_MARKERS = ("Ã", "Â", "â€", "â‚", "Å")


def looks_garbled(text: str | None) -> bool:
    return bool(text) and any(m in text for m in _MARKERS)


def _cp1252_roundtrip(text: str, max_rounds: int = 3) -> str:
    """Undo 'utf-8 bytes decoded as cp1252', repeated for double encoding. Stops at the first failure."""
    for _ in range(max_rounds):
        if not looks_garbled(text):
            break
        try:
            fixed = text.encode("cp1252").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            break
        text = fixed
    return text


def repair_text(text: str | None) -> str | None:
    """Return text with encoding damage repaired. Clean text is returned unchanged."""
    if not text or not looks_garbled(text):
        return text
    if _ftfy_fix is not None:
        fixed = _ftfy_fix(text)
        if not looks_garbled(fixed):
            return fixed
        text = fixed
    return _cp1252_roundtrip(text)
