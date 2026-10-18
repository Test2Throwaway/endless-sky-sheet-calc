"""Read which outfits are in play from an outfits-in-play.md file."""

import re
from dataclasses import dataclass
from pathlib import Path

DEFAULT_IN_PLAY = Path(__file__).resolve().parents[1] / "data" / "outfits-in-play.md"

_ENTRY = re.compile(r"^- (.+?) — (.+)$", re.M)
_AT_MOST = re.compile(r",?\s*at most (\d+)")


@dataclass(frozen=True)
class Availability:
    source: str          # e.g. "sold", "taken from ships only (plunder, capture)"
    max_count: int | None  # None means unlimited


def load_in_play(path=DEFAULT_IN_PLAY):
    """Return {outfit name: Availability} for every outfit listed as in play."""
    text = Path(path).read_text(encoding="utf-8")
    in_play_section = text.split("## Not in play")[0]
    result = {}
    for name, status in _ENTRY.findall(in_play_section):
        limit = _AT_MOST.search(status)
        source = _AT_MOST.sub("", status).strip()
        result[name] = Availability(source, int(limit.group(1)) if limit else None)
    return result
