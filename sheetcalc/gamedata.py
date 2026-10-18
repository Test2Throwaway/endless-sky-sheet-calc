"""Read outfit definitions from the Endless Sky data files."""

import os
import re
from pathlib import Path

# Game attributes are stored per frame; the game runs at 60 frames per second.
FPS = 60

DEFAULT_DATA_DIR = Path(os.environ.get(
    "ES_DATA_DIR", Path(__file__).resolve().parents[2] / "endless-sky" / "data"))

# A token is a "double-quoted" string, a `backtick-quoted` string, or a bare word.
_TOKEN = re.compile(r'"([^"]*)"|`([^`]*)`|(\S+)')


def _tokens(line):
    return [m.group(m.lastindex) for m in _TOKEN.finditer(line)]


def load_outfits(data_dir=DEFAULT_DATA_DIR):
    """Return {outfit name: {attribute: value}} for every top-level outfit.

    Only first-level attributes are kept. Numeric values are floats, others strings.
    """
    outfits = {}
    for path in sorted(Path(data_dir).rglob("*.txt")):
        current = None
        for raw in path.read_text(encoding="utf-8").splitlines():
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                continue
            indent = len(raw) - len(raw.lstrip("\t"))
            tokens = _tokens(stripped)
            if indent == 0:
                current = None
                if tokens[0] == "outfit" and len(tokens) > 1:
                    current = outfits.setdefault(tokens[1], {"_file": str(path.relative_to(data_dir))})
            elif indent == 1 and current is not None and len(tokens) >= 2:
                try:
                    current[tokens[0]] = float(tokens[1])
                except ValueError:
                    current.setdefault(tokens[0], tokens[1])
    return outfits


def space(outfit):
    """Outfit space used, as a positive number."""
    return -outfit.get("outfit space", 0.)


def per_second(outfit, attribute):
    return outfit.get(attribute, 0.) * FPS
