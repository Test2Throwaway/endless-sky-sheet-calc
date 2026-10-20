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

    First-level attributes are kept as-is: numeric values are floats, others strings. A
    weapon's sub-block is kept under "_weapon" the same way, except that bare flags (e.g.
    "safe") are 1 and submunitions are a list of (name, count) under "submunition".
    """
    outfits = {}
    for path in sorted(Path(data_dir).rglob("*.txt")):
        current = weapon = None
        for raw in path.read_text(encoding="utf-8").splitlines():
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                continue
            indent = len(raw) - len(raw.lstrip("\t"))
            tokens = _tokens(stripped)
            if indent == 0:
                current = weapon = None
                if tokens[0] == "outfit" and len(tokens) > 1:
                    current = outfits.setdefault(tokens[1], {"_file": str(path.relative_to(data_dir))})
            elif current is None:
                continue
            elif indent == 1:
                weapon = None
                if tokens == ["weapon"]:
                    weapon = current.setdefault("_weapon", {})
                elif len(tokens) >= 2:
                    _store(current, tokens)
            elif indent == 2 and weapon is not None:
                if tokens[0] == "submunition" and len(tokens) >= 2:
                    count = float(tokens[2]) if len(tokens) >= 3 else 1.
                    weapon.setdefault("submunition", []).append((tokens[1], count))
                elif len(tokens) == 1:
                    weapon[tokens[0]] = 1.
                else:
                    _store(weapon, tokens)
    return outfits


def _store(block, tokens):
    try:
        block[tokens[0]] = float(tokens[1])
    except ValueError:
        block.setdefault(tokens[0], tokens[1])


def space(outfit):
    """Outfit space used, as a positive number."""
    return -outfit.get("outfit space", 0.)


def per_second(outfit, attribute):
    return outfit.get(attribute, 0.) * FPS
