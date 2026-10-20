"""Strict dominance: drop an outfit only if another is at least as good in every way.

Valid for every design the optimizer can be asked for, because it never trades one stat against another.
B beats A only if all of these hold:
- same category;
- every attribute (and weapon key) with a direction is at least as good on B and strictly better on one;
- every presence attribute is present on both or on neither;
- every other attribute is equal (unknown attributes therefore block);
- B is no harder to get than A and has no tighter copy limit.

Identical outfits: the easier one to get is kept, then the first by name.

Whole multiples: a ship's attributes are the sum of its outfits', so k copies of B beat one A if the scaled
attributes pass the same test. That catches "two small thrusters are better than one big one". It is not used
for weapons (each copy needs its own gun port or turret mount, which the capacity check already rules out, and
weapon keys don't add up) or for Hand to Hand outfits (one per crew member).

Outfits with nothing but a footprint (space, mass, crew) are never dropped: their value is their identity.
"""

from dataclasses import dataclass

from .attributes import (FOOTPRINT, PRESENCE, TURRET_TURN_DEFAULT, WEAPON_DEFAULTS, WEAPON_PRESENCE, direction,
                         weapon_direction)

# Categories that are not designed with (story items, licences, minerals) are left alone.
NOT_DESIGNABLE = {"Licenses", "Minerals", "Special", "Unique"}

# Never scaled: one per crew member, so k copies aren't k times as good.
NOT_SCALABLE = {"Hand to Hand"}
MAX_MULTIPLE = 10

# Availability, easiest first.
TIER_ORDER = ["sold", "taken", "all"]

JUMP_FUEL_DEFAULTS = (("jump drive", 200.), ("scram drive", 150.), ("hyperdrive", 100.))


def tier_of(availability):
    if availability.source == "sold":
        return "sold"
    if availability.source.startswith("taken from ships"):
        return "taken"
    return "all"


def _effective(outfit):
    """Top-level attributes and weapon keys with the game's defaults applied."""
    attrs = {k: v for k, v in outfit.items() if k != "_weapon" and direction(k) != 0}
    if "jump fuel" not in attrs:
        for drive, fuel in JUMP_FUEL_DEFAULTS:
            if attrs.get(drive):
                attrs["jump fuel"] = fuel
                break
    weapon = None
    if "_weapon" in outfit:
        weapon = {k: v for k, v in outfit["_weapon"].items() if weapon_direction(k) != 0}
        for key, default in WEAPON_DEFAULTS.items():
            weapon.setdefault(key, default)
        if (outfit.get("category") == "Turrets" and not weapon.get("turret turn")
                and not weapon.get("anti-missile") and not weapon.get("tractor beam")):
            weapon["turret turn"] = TURRET_TURN_DEFAULT
    return attrs, weapon


def _compare(a, b, direction_of, presence):
    """Compare two attribute dicts. Returns None if b can't beat a, else whether b is strictly better
    somewhere (False means equal on everything compared)."""
    strictly = False
    for key in a.keys() | b.keys():
        va, vb = a.get(key, 0.), b.get(key, 0.)
        d = direction_of(key)
        if d == 0:
            continue
        if key in presence and bool(va) != bool(vb):
            return None
        if d is None or not isinstance(va, (int, float)) or not isinstance(vb, (int, float)):
            if va != vb:
                return None
            continue
        if d * (vb - va) < -1e-9:
            return None
        if d * (vb - va) > 1e-9:
            strictly = True
    return strictly


@dataclass(frozen=True)
class _Candidate:
    name: str
    category: str
    attrs: dict
    weapon: dict | None
    tier: int
    copy_limit: float  # infinity when unlimited


def _candidates(outfits, availability):
    out = []
    for name, a in availability.items():
        outfit = outfits[name]
        category = outfit.get("category", "")
        if category in NOT_DESIGNABLE or outfit.get("installable", 0) < 0:
            continue
        attrs, weapon = _effective(outfit)
        limit = a.max_count if a.max_count is not None else float("inf")
        if outfit.get("unique"):
            limit = min(limit, 1)
        out.append(_Candidate(name, category, attrs, weapon, TIER_ORDER.index(tier_of(a)), limit))
    return out


def _scaled(attrs, k):
    return {key: v * k if isinstance(v, (int, float)) else v for key, v in attrs.items()}


def _identity_only(c):
    return c.weapon is None and all(k in FOOTPRINT or direction(k) == 0 or k == "category" for k in c.attrs)


def _beats_by_multiple(b, a):
    """The smallest k >= 2 such that k copies of b strictly beat one a, or None."""
    if (b.category != a.category or b.category in NOT_SCALABLE or a.weapon is not None or b.weapon is not None
            or b.tier > a.tier):
        return None
    space_a, space_b = -a.attrs.get("outfit space", 0.), -b.attrs.get("outfit space", 0.)
    if space_b <= 0:
        return None
    for k in range(2, min(MAX_MULTIPLE, int(space_a // space_b)) + 1):
        if k > b.copy_limit:
            return None
        result = _compare(a.attrs, _scaled(b.attrs, k), direction, PRESENCE)
        if result:
            return k
    return None


def _beats(b, a):
    """Whether b strictly dominates a (or ties with it and wins the tie-break)."""
    if b.category != a.category or b.tier > a.tier or b.copy_limit < a.copy_limit:
        return False
    if (a.weapon is None) != (b.weapon is None):
        return False
    top = _compare(a.attrs, b.attrs, direction, PRESENCE)
    if top is None:
        return False
    strictly = top
    if a.weapon is not None:
        w = _compare(a.weapon, b.weapon, weapon_direction, WEAPON_PRESENCE)
        if w is None:
            return False
        strictly = strictly or w
    if strictly:
        return True
    # Identical: keep the easier to get, then the first by name.
    return (b.tier, -b.copy_limit, b.name) < (a.tier, -a.copy_limit, a.name)


def strict_dominance(outfits, availability):
    """Return (considered outfit names, {dropped outfit: {outfit that beats it: copies needed}})."""
    candidates = _candidates(outfits, availability)
    by_category = {}
    for c in candidates:
        by_category.setdefault(c.category, []).append(c)
    dropped = {}
    for group in by_category.values():
        for a in group:
            if _identity_only(a):
                continue
            beaters = {}
            for b in group:
                if b is a:
                    continue
                if _beats(b, a):
                    beaters[b.name] = 1
                elif (k := _beats_by_multiple(b, a)) is not None:
                    beaters[b.name] = k
            if beaters:
                dropped[a.name] = dict(sorted(beaters.items()))
    return [c.name for c in candidates], dropped
