"""Engine passes: compensated dominance per solar case (docs/pruner-design.md, sections 5 and 6).

Every ship pays for its engines' energy and heat with power plant and cooling, so those are traded for outfit space
at the solar case's rates. A compensated cost is

    outfit space + energy rate × energy/s + heat rate × heat/s

with thrusting at 70% and turning at 30% duty (the optimizer's cruise duty cycles), plus any steady energy
generation, consumption and heat generation on the outfit. The rates come from the case's power plant search at
each reference ship load; their range is a box, and B beats A only if B's cost is no higher at every corner.

Everything else uses the strict rules (attributes.py): thrust, turn, reverse thrust higher; engine capacity, mass
and every other attribute as in strict dominance; afterburners, torches and other classes as presence keys.
Reverse thrusting energy and heat stay strict (reversing is not part of cruise). Whole copies of a smaller engine
count, as in strict dominance. A drop is valid for every request in that solar case.
"""

from itertools import product

from .attributes import PRESENCE, direction
from .strict import MAX_MULTIPLE, _candidates, _compare, _scaled

FPS = 60.
THRUST_DUTY, TURN_DUTY = .7, .3
# Attribute -> (resource, per-second weight). Positive energy generation lowers the energy bill.
TRADED = {
    "thrusting energy": ("energy", THRUST_DUTY * FPS),
    "thrusting heat": ("heat", THRUST_DUTY * FPS),
    "turning energy": ("energy", TURN_DUTY * FPS),
    "turning heat": ("heat", TURN_DUTY * FPS),
    "energy consumption": ("energy", FPS),
    "energy generation": ("energy", -FPS),
    "heat generation": ("heat", FPS),
}


def _load(attrs):
    """(energy/s, heat/s) this outfit adds to the ship at cruise duty."""
    load = {"energy": 0., "heat": 0.}
    for key, (resource, weight) in TRADED.items():
        load[resource] += attrs.get(key, 0.) * weight
    return load["energy"], load["heat"]


def _costs(attrs, corners):
    """Compensated cost at each corner of the rate box."""
    space = -attrs.get("outfit space", 0.)
    energy, heat = _load(attrs)
    return [space + e * energy + h * heat for e, h in corners]


def _untraded(attrs):
    return {k: v for k, v in attrs.items() if k not in TRADED and k != "outfit space"}


def _compensated_beats(a, b_attrs, corners):
    """None if b can't beat a; otherwise whether b is strictly better somewhere."""
    rest = _compare(_untraded(a.attrs), _untraded(b_attrs), direction, PRESENCE)
    if rest is None:
        return None
    ca, cb = _costs(a.attrs, corners), _costs(b_attrs, corners)
    if any(y > x + 1e-9 for x, y in zip(ca, cb)):
        return None
    return rest or any(y < x - 1e-9 for x, y in zip(ca, cb))


def rate_box(prices):
    """Corners of the rate box from {reference load: {"energy": rate, "heat": rate}}."""
    energy = [p["energy"] for p in prices.values()]
    heat = [p["heat"] for p in prices.values()]
    return list(product((min(energy), max(energy)), (min(heat), max(heat))))


def engine_dominance(outfits, availability, corners):
    """Return (engines considered, {dropped engine: {engine that beats it: copies needed}})."""
    group = [c for c in _candidates(outfits, availability) if c.category == "Engines"]
    dropped = {}
    for a in group:
        beaters = {}
        for b in group:
            if b is a or b.tier > a.tier:
                continue
            if b.copy_limit >= a.copy_limit:
                result = _compensated_beats(a, b.attrs, corners)
                if result or (result is False and (b.tier, -b.copy_limit, b.name) < (a.tier, -a.copy_limit, a.name)):
                    beaters[b.name] = 1
                    continue
            space_a, space_b = -a.attrs.get("outfit space", 0.), -b.attrs.get("outfit space", 0.)
            if space_b <= 0:
                continue
            for k in range(2, min(MAX_MULTIPLE, int(space_a // space_b)) + 1):
                if k > b.copy_limit:
                    break
                if _compensated_beats(a, _scaled(b.attrs, k), corners):
                    beaters[b.name] = k
                    break
        if beaters:
            dropped[a.name] = dict(sorted(beaters.items()))
    return [c.name for c in group], dropped
