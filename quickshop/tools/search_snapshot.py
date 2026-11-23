# Saved search results, so the same query gives the same listings on every run.
# Live runs save each good search here. Replay runs (--frozen) only read from here and never call Firecrawl search.
from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_SNAPSHOT_PATH = ".cache/search_snapshot.json"

_lock = threading.Lock()


def snapshot_path() -> Path:
    return Path(os.getenv("QUICKSHOP_SEARCH_SNAPSHOT") or DEFAULT_SNAPSHOT_PATH)


def replay_on() -> bool:
    return os.getenv("QUICKSHOP_SEARCH_REPLAY", "") not in ("", "0")


def snapshot_key(query: str, max_results: int) -> str:
    # "Black  Jeans " and "black jeans" are the same search
    return f"{' '.join(query.lower().split())}|{max_results}"


def _read(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def load(query: str, max_results: int) -> list[dict] | None:
    """Saved listings for this search, or None if it was never saved."""
    with _lock:
        entry = _read(snapshot_path()).get(snapshot_key(query, max_results))
    return None if entry is None else entry["listings"]


def save(query: str, max_results: int, listings: list[dict]) -> None:
    """Save the listings of a search that worked. Errors are never saved."""
    path = snapshot_path()
    with _lock:
        data = _read(path)
        data[snapshot_key(query, max_results)] = {
            "query": query,
            "max_results": max_results,
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "listings": listings,
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        # write to a temp file first so a crash never leaves half a file
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(data, indent=2))
        tmp.replace(path)
