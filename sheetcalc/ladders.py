"""Exact passive-cooling and energy-generation ladders.

A ladder answers "what is the least outfit space that provides X?", using only
whole outfits. Outfits that never appear on a ladder are obsolete: some other
in-play combination always does at least as well in no more space.
"""

import bisect
from collections import Counter
from dataclasses import dataclass

from .gamedata import per_second, space
from .settings import SOLAR_ENERGY_CASE, SOLAR_HEAT_CASE, SOLAR_MULTIPLIER


@dataclass(frozen=True)
class Item:
    name: str
    space: int
    max_count: int | None  # None means unlimited
    cooling: float = 0.  # passive cooling per second
    energy: float = 0.   # net energy per second
    heat: float = 0.     # heat per second


def _max_count(name, outfit, availability):
    limit = availability[name].max_count
    if outfit.get("unique"):
        limit = 1 if limit is None else min(limit, 1)
    return limit


# ---------------------------------------------------------------- cooling

def passive_coolers(outfits, availability):
    """In-play Systems outfits with passive cooling. Only the passive part of
    hybrid coolers counts; active cooling is out of scope for now."""
    items = []
    for name in availability:
        outfit = outfits[name]
        if outfit.get("category") == "Systems" and outfit.get("cooling", 0) > 0 and space(outfit) > 0:
            items.append(Item(name, int(space(outfit)), _max_count(name, outfit, availability),
                              cooling=per_second(outfit, "cooling")))
    return items


class CoolingLadder:
    def __init__(self, coolers, max_space=1200):
        self.coolers = coolers
        # best[s] = most cooling that fits in s space; combo[s] = how.
        best = [0.] * (max_space + 1)
        combo = [Counter() for _ in range(max_space + 1)]
        for item in coolers:
            copies = [1] * item.max_count if item.max_count is not None else None
            if copies is None:
                spaces = range(item.space, max_space + 1)
                passes = [spaces]
            else:
                passes = [range(max_space, item.space - 1, -1) for _ in copies]
            for spaces in passes:
                for s in spaces:
                    candidate = best[s - item.space] + item.cooling
                    if candidate > best[s]:
                        best[s] = candidate
                        combo[s] = combo[s - item.space] + Counter({item.name: 1})
        # Make best non-decreasing in space (leftover space can go unused).
        for s in range(1, max_space + 1):
            if best[s - 1] >= best[s]:
                best[s], combo[s] = best[s - 1], combo[s - 1]
        self.best = best
        self.combo = combo

    def space_for(self, heat):
        """Least outfit space whose passive cooling covers `heat` per second."""
        if heat <= 0:
            return 0
        s = bisect.bisect_left(self.best, heat - 1e-9)
        if s >= len(self.best):
            raise ValueError(f"heat {heat} exceeds ladder range")
        return s

    def rungs(self):
        """(space, cooling, combo) for each space where cooling strictly improves."""
        out = []
        for s in range(1, len(self.best)):
            if self.best[s] > self.best[s - 1]:
                out.append((s, self.best[s], self.combo[s]))
        return out

    def used(self):
        return {name for _, _, combo in self.rungs() for name in combo}


# ---------------------------------------------------------------- energy

def _generator_item(name, space_, egen, solar, heat, solar_heat, max_count):
    energy = egen + solar * SOLAR_MULTIPLIER[SOLAR_ENERGY_CASE]
    heat = heat + solar_heat * SOLAR_MULTIPLIER[SOLAR_HEAT_CASE]
    return Item(name, int(space_), max_count, energy=energy, heat=heat)


def generators(outfits, availability):
    """In-play Power outfits that generate energy, plus slot-based combinations.

    Slot-limited outfits are folded into composites with the outfit that
    provides their slots: Solar Battery + n Solar Cells, and reactors with
    "reactor upgrades" + k Reactor Overclockers. Hull-slot outfits (anchor
    points) are excluded, since only some hulls have them.
    """
    def stats(name):
        o = outfits[name]
        return (space(o), per_second(o, "energy generation") - per_second(o, "energy consumption"),
                per_second(o, "solar collection"), per_second(o, "heat generation"),
                per_second(o, "solar heat"))

    items, excluded = [], {}
    for name in availability:
        o = outfits[name]
        if o.get("category") != "Power":
            continue
        _, energy, solar, _, _ = stats(name)
        if energy <= 0 and solar <= 0:
            continue
        if o.get("anchor point", 0) < 0:
            excluded[name] = "needs hull anchor points"
            continue
        if o.get("solar cell", 0) < 0 or o.get("reactor upgrades", 0) < 0:
            continue  # handled as part of a composite below
        items.append(_generator_item(name, *stats(name), _max_count(name, o, availability)))

    # Solar Battery + n Solar Cells.
    if "Solar Battery" in availability and "Solar Cell" in availability:
        battery, cell = outfits["Solar Battery"], stats("Solar Cell")
        for n in range(1, int(battery.get("solar cell", 0)) + 1):
            items.append(_generator_item(
                f"Solar Battery + {n} Solar Cell{'s' if n > 1 else ''}",
                space(battery) + n * cell[0], n * cell[1], n * cell[2], n * cell[3], n * cell[4],
                _max_count("Solar Battery", battery, availability)))

    # Reactor + k Reactor Overclockers.
    if "Reactor Overclocker" in availability:
        oc_outfit = outfits["Reactor Overclocker"]
        oc, slots_per = stats("Reactor Overclocker"), -oc_outfit["reactor upgrades"]
        for name in availability:
            slots = outfits[name].get("reactor upgrades", 0)
            if slots <= 0:
                continue
            base = stats(name)
            for k in range(1, int(slots // slots_per) + 1):
                items.append(_generator_item(
                    f"{name} + {k} Reactor Overclocker{'s' if k > 1 else ''}",
                    *(b + k * x for b, x in zip(base, oc)),
                    _max_count(name, outfits[name], availability)))
    return items, excluded


def _pareto(states):
    """Keep (heat, energy, combo) states not beaten on both heat and energy."""
    states.sort(key=lambda st: (st[0], -st[1]))
    kept, best_energy = [], -1.
    for st in states:
        if st[1] > best_energy + 1e-9:
            kept.append(st)
            best_energy = st[1]
    return kept


class EnergyLadder:
    """Least total space (generators + passive cooling for their heat, plus any
    `base_heat` the rest of the ship needs cooled) for each energy level."""

    def __init__(self, items, cooling, max_generator_space=400, base_heat=0.):
        self.items, self.cooling, self.base_heat = items, cooling, base_heat
        n = max_generator_space
        # states[s]: Pareto set of (heat, energy, combo) using exactly s generator space.
        states = [[] for _ in range(n + 1)]
        states[0] = [(0., 0., ())]
        for index, item in enumerate(items):
            if item.max_count is None:
                passes = [range(item.space, n + 1)]
            else:
                passes = [range(n, item.space - 1, -1)] * item.max_count
            for spaces in passes:
                for s in spaces:
                    prev = states[s - item.space]
                    if not prev:
                        continue
                    added = [(h + item.heat, e + item.energy, c + (index,)) for h, e, c in prev]
                    states[s] = _pareto(states[s] + added)
        self.rungs = self._rungs(states)

    def _rungs(self, states):
        by_total = {}
        for s, group in enumerate(states):
            for heat, energy, combo in group:
                if not combo:
                    continue
                total = s + self.cooling.space_for(heat + self.base_heat) - self.cooling.space_for(self.base_heat)
                if total not in by_total or energy > by_total[total][0]:
                    by_total[total] = (energy, s, heat, combo)
        rungs, best = [], 0.
        for total in sorted(by_total):
            energy, s, heat, combo = by_total[total]
            if energy > best + 1e-9:
                names = Counter(self.items[i].name for i in combo)
                rungs.append((total, energy, s, heat, names))
                best = energy
        return rungs

    def space_for(self, energy):
        """Least total space giving at least `energy` per second."""
        for total, e, *_ in self.rungs:
            if e >= energy - 1e-9:
                return total
        raise ValueError(f"energy {energy} exceeds ladder range")

    def used(self):
        return {name for *_, combo in self.rungs for name in combo}
