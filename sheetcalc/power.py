"""Joint power and cooling plant: generators, passive coolers and active coolers.

Active cooling makes power and cooling depend on each other: active coolers draw
energy, and the generators that supply it make heat. Instead of pricing one and
then the other, `PowerPlant.solve` searches whole-outfit combinations of all
three at once for the least total space that covers a given energy draw and heat
load, so the loop never has to be unrolled.

Game rules used (Ship.cpp): passive cooling applies first. At heat fraction f, the
active coolers together remove f × (total active cooling) per second and draw
f × (total cooling energy). So the energy per unit of heat removed is
(total cooling energy) / (total active cooling), whatever f is, and capacity is
limited by the heat fraction the design is willing to run at.
"""

import bisect
from collections import Counter
from dataclasses import dataclass

import numpy as np

from .gamedata import per_second, space
from .ladders import CoolingLadder, generator_states, generators, passive_coolers, _max_count
from .settings import ACTIVE_COOLING_HEAT_FRACTION, DEFAULT_SCENARIO


@dataclass(frozen=True)
class ActiveCooler:
    name: str
    space: int
    max_count: int | None
    active: float           # active cooling per second at full heat
    cooling_energy: float   # energy per second at full heat
    passive: float = 0.     # passive cooling per second (hybrid coolers)
    consumption: float = 0.  # constant energy draw per second


def active_coolers(outfits, availability):
    items = []
    for name in availability:
        o = outfits[name]
        if o.get("category") == "Systems" and o.get("active cooling", 0) > 0 and space(o) > 0:
            items.append(ActiveCooler(
                name, int(space(o)), _max_count(name, o, availability),
                per_second(o, "active cooling"), per_second(o, "cooling energy"),
                per_second(o, "cooling"), per_second(o, "energy consumption")))
    return items


def _dominates(a, b):
    """State tuples are (space, active, cooling_energy, passive, consumption, combo)."""
    return (a[0] <= b[0] and a[1] >= b[1] - 1e-9 and a[2] <= b[2] + 1e-9
            and a[3] >= b[3] - 1e-9 and a[4] <= b[4] + 1e-9)


def _prune(states):
    states.sort(key=lambda st: (st[0], -st[1], st[2]))
    kept = []
    for st in states:
        if not any(_dominates(k, st) for k in kept):
            kept.append(st)
    return kept


def _generator_front(states):
    """(space, heat, energy, combo) for generator combinations that no combination
    of no more space beats on both heat and energy."""
    flat = sorted(((s, h, e, combo) for s, group in enumerate(states) for h, e, combo in group),
                  key=lambda st: (st[0], st[1], -st[2]))
    front = []
    # Staircase of kept states: heats ascending with energies strictly ascending,
    # so the best energy at heat <= h is the entry just left of h.
    heats, energies = [], []
    for st in flat:
        _, h, e, _ = st
        i = bisect.bisect_right(heats, h)
        if i and energies[i - 1] >= e - 1e-9:
            continue
        front.append(st)
        j = i
        while j < len(heats) and energies[j] <= e:
            j += 1
        heats[i:j], energies[i:j] = [h], [e]
    return front


def active_states(coolers, max_space):
    """Non-dominated combinations of active coolers, including the empty one."""
    by_space = [[] for _ in range(max_space + 1)]
    by_space[0] = [(0, 0., 0., 0., 0., ())]
    for index, c in enumerate(coolers):
        passes = ([range(c.space, max_space + 1)] if c.max_count is None
                  else [range(max_space, c.space - 1, -1)] * c.max_count)
        for spaces in passes:
            for s in spaces:
                prev = by_space[s - c.space]
                if not prev:
                    continue
                added = [(s, a + c.active, e + c.cooling_energy, p + c.passive, k + c.consumption, combo + (index,))
                         for _, a, e, p, k, combo in prev]
                by_space[s] = _prune(by_space[s] + added)
    return _prune([st for group in by_space for st in group])


@dataclass
class Plant:
    space: int
    generator_space: int
    passive_space: int
    active_space: int
    generators: Counter
    passive: Counter
    active: Counter
    energy: float           # generated energy per second
    heat: float             # heat to remove: load + generators
    active_heat: float      # heat removed by active cooling
    active_energy: float    # energy the active coolers draw


class PowerPlant:
    def __init__(self, passive, generator_items, active_items, max_generator_space=400, max_active_space=48,
                 heat_fraction=ACTIVE_COOLING_HEAT_FRACTION):
        """`passive` is a CoolingLadder; the item lists are the generators and active
        coolers allowed in the plant."""
        self.passive = passive
        self.generator_items, self.active_items = list(generator_items), list(active_items)
        self.heat_fraction = heat_fraction
        self.max_generator_space, self.max_active_space = max_generator_space, max_active_space
        # Sorted by space, so the empty combination (no active cooling) comes first.
        self.active = sorted(active_states(self.active_items, max_active_space), key=lambda st: st[0])
        # Sorted by space, so solve() can stop at the best total found so far.
        self.generator_front = _generator_front(generator_states(self.generator_items, max_generator_space))
        g = self.generator_front
        self._gen_space = np.array([st[0] for st in g])
        self._gen_heat = np.array([st[1] for st in g])
        self._gen_energy = np.array([st[2] for st in g])
        self._passive_best = np.array(self.passive.best)

    @classmethod
    def from_game(cls, outfits, availability, use_active=True, scenario=DEFAULT_SCENARIO, **kwargs):
        gens, excluded = generators(outfits, availability, scenario)
        kwargs.setdefault("heat_fraction", scenario.heat_fraction)
        plant = cls(CoolingLadder(passive_coolers(outfits, availability)), gens,
                    active_coolers(outfits, availability) if use_active else [], **kwargs)
        plant.excluded = excluded
        return plant

    def without(self, names):
        """A copy of this plant with the named generators and active coolers removed."""
        names = set(names)
        return PowerPlant(self.passive, [i for i in self.generator_items if i.name not in names],
                          [c for c in self.active_items if c.name not in names],
                          self.max_generator_space, self.max_active_space, self.heat_fraction)

    def prices(self, energy_load, heat_load, spread=.25):
        """Marginal (space per energy/s, space per heat/s) around a load, from a
        least-squares plane through solutions on a 3×3 grid of ±spread. Whole
        outfits make the exact cost a staircase; the plane gives its slope."""
        rows, totals = [], []
        for de in (-spread, 0, spread):
            for dh in (-spread, 0, spread):
                e, h = energy_load * (1 + de), heat_load * (1 + dh)
                plant = self.solve(e, h)
                if plant is not None:
                    rows.append((1., e, h))
                    totals.append(plant.space)
        (_, energy_price, heat_price), *_ = np.linalg.lstsq(np.array(rows), np.array(totals, dtype=float), rcond=None)
        return float(energy_price), float(heat_price)

    def solve(self, energy_load, heat_load):
        """Least-space plant covering `energy_load` energy/s and `heat_load` heat/s
        for the rest of the ship. Returns a Plant, or None if out of range."""
        f = self.heat_fraction
        best, best_key = None, None
        for sa, active, cooling_energy, passive, consumption, act_combo in self.active:
            # Only generator combinations small enough to beat the best total so far.
            n = len(self._gen_space) if best is None else int(np.searchsorted(self._gen_space, best - sa))
            if n == 0:
                break
            spare = self._gen_energy[:n] - energy_load
            heat = heat_load + self._gen_heat[:n]
            usable = spare >= consumption
            remaining = np.maximum(heat - passive, 0.)
            cap = np.full_like(remaining, active * f)
            if cooling_energy > 0:
                cap = np.minimum(cap, (spare - consumption) * active / cooling_energy)
            active_heat = np.minimum(np.maximum(cap, 0.), remaining)
            passive_need = remaining - active_heat
            passive_space = np.searchsorted(self._passive_best, passive_need - 1e-9)
            usable &= passive_space < len(self._passive_best)
            total = np.where(usable, self._gen_space[:n] + sa + passive_space, np.iinfo(np.int64).max)
            i = int(np.argmin(total))
            if usable[i] and (best is None or total[i] < best):
                best = int(total[i])
                act_energy = (active_heat[i] * cooling_energy / active if active else 0.) + consumption
                best_key = (i, int(passive_space[i]), sa, act_combo, float(active_heat[i]), act_energy)
        if best is None:
            return None
        i, sp, sa, act_combo, active_heat, active_energy = best_key
        s, h, e, gen_combo = self.generator_front[i]
        return Plant(best, s, sp, sa,
                     Counter(self.generator_items[j].name for j in gen_combo),
                     self.passive.combo[sp],
                     Counter(self.active_items[j].name for j in act_combo),
                     e, heat_load + h, active_heat, active_energy)
