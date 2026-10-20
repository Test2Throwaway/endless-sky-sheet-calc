"""Engine passes: compensated dominance per solar case (docs/pruner-design.md, sections 5 and 6).

Every ship pays for its engines' energy and heat with power plant and cooling, so those are traded for outfit space
at the solar case's rates. A compensated cost is

    outfit space + energy rate × energy/s + heat rate × heat/s

for the thrusting and turning energy and heat, plus any steady energy generation, consumption and heat generation
on the outfit. How much a ship thrusts and turns is not known, so thrust duty and turn duty are each taken at 0%
and at 100%, independently; the cost is linear in each duty, so a drop that holds at those corners holds at every
duty in between. The rates come from the case's power plant search at each reference ship load; their range is a
box, and B beats A only if B's cost is no higher at every corner (rates × duties).

Everything else uses the strict rules (attributes.py): thrust, turn, reverse thrust higher; engine capacity, mass
and every other attribute as in strict dominance; afterburners, torches and other classes as presence keys.
Reverse thrusting energy and heat stay strict (reversing is not part of cruise). Whole copies of a smaller engine
count, as in strict dominance. A drop is valid for every request in that solar case.
"""

from itertools import product

from .attributes import PRESENCE, direction
from .strict import MAX_MULTIPLE, _candidates, _compare, _scaled

FPS = 60.
DUTIES = (0., 1.)
# Traded attribute -> (resource, per-second weight, duty group). Steady power is always on (no duty group);
# positive energy generation lowers the energy bill. Each duty group is taken at 0% and at 100%, independently.
STEADY_POWER = {
    "energy consumption": ("energy", FPS, None),
    "energy generation": ("energy", -FPS, None),
    "heat generation": ("heat", FPS, None),
}
TRADED = {
    "thrusting energy": ("energy", FPS, "thrust"),
    "thrusting heat": ("heat", FPS, "thrust"),
    "turning energy": ("energy", FPS, "turn"),
    "turning heat": ("heat", FPS, "turn"),
    **STEADY_POWER,
}


def _costs(attrs, corners, traded):
    """Compensated cost at each corner (energy rate, heat rate, {duty group: duty})."""
    space = -attrs.get("outfit space", 0.)
    costs = []
    for energy_rate, heat_rate, duty in corners:
        rate = {"energy": energy_rate, "heat": heat_rate}
        costs.append(space + sum(attrs.get(key, 0.) * weight * (duty[group] if group else 1.) * rate[resource]
                                 for key, (resource, weight, group) in traded.items()))
    return costs


def _compensated_beats(a, b_attrs, corners, traded):
    """None if b can't beat a; otherwise whether b is strictly better somewhere."""
    untraded = lambda attrs: {k: v for k, v in attrs.items() if k not in traded and k != "outfit space"}
    rest = _compare(untraded(a.attrs), untraded(b_attrs), direction, PRESENCE)
    if rest is None:
        return None
    ca, cb = _costs(a.attrs, corners, traded), _costs(b_attrs, corners, traded)
    if any(y > x + 1e-9 for x, y in zip(ca, cb)):
        return None
    return rest or any(y < x - 1e-9 for x, y in zip(ca, cb))


def rate_box(prices, traded=TRADED):
    """Corners (energy rate, heat rate, {duty group: duty}) from {reference load: {"energy": rate, "heat": rate}}:
    the lowest and highest rate of each resource, and each duty group of `traded` at 0% and 100%."""
    energy = [p["energy"] for p in prices.values()]
    heat = [p["heat"] for p in prices.values()]
    groups = sorted({g for _, _, g in traded.values() if g})
    duties = [dict(zip(groups, d)) for d in product(DUTIES, repeat=len(groups))]
    return list(product((min(energy), max(energy)), (min(heat), max(heat)), duties))


def compensated_dominance(outfits, availability, corners, traded, select):
    """Compensated dominance within each category among the candidates `select` accepts.
    Return (outfits considered, {dropped outfit: {outfit that beats it: copies needed}})."""
    group = [c for c in _candidates(outfits, availability) if select(c)]
    dropped = {}
    for a in group:
        beaters = {}
        for b in group:
            if b is a or b.category != a.category or b.tier > a.tier:
                continue
            if b.copy_limit >= a.copy_limit:
                result = _compensated_beats(a, b.attrs, corners, traded)
                if result or (result is False and (b.tier, -b.copy_limit, b.name) < (a.tier, -a.copy_limit, a.name)):
                    beaters[b.name] = 1
                    continue
            space_a, space_b = -a.attrs.get("outfit space", 0.), -b.attrs.get("outfit space", 0.)
            if space_b <= 0:
                continue
            for k in range(2, min(MAX_MULTIPLE, int(space_a // space_b)) + 1):
                if k > b.copy_limit:
                    break
                if _compensated_beats(a, _scaled(b.attrs, k), corners, traded):
                    beaters[b.name] = k
                    break
        if beaters:
            dropped[a.name] = dict(sorted(beaters.items()))
    return [c.name for c in group], dropped


def engine_dominance(outfits, availability, corners):
    """Return (engines considered, {dropped engine: {engine that beats it: copies needed}})."""
    return compensated_dominance(outfits, availability, corners, TRADED, lambda c: c.category == "Engines")
