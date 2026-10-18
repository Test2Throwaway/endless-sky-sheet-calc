"""Find which power and cooling outfits a designer never needs.

Three passes, each removing outfits the next pass then doesn't have to consider:

1. Dumb: strictly dominated. Another outfit is no bigger and no worse on any stat
   (and no more restricted in how many you can get).
2. Ladder: passive coolers that never appear on the exact passive-cooling ladder.
   Passive coolers only provide passive cooling, so the ladder is exact for them.
3. Smart: generators and active coolers judged by the joint power plant. Over a grid
   of ship loads (energy draw, heat), an outfit is obsolete if banning it never makes
   the best plant bigger. Outfits that never appear in a best plant go first, all at
   once; then each remaining outfit is banned in turn and kept only if that costs
   space somewhere. Ties are settled in favour of outfits that are easier to get.

"Never" means "at none of the loads tested"; see OBSOLESCENCE_ENERGY / _HEAT.
"""

from collections import Counter
from dataclasses import dataclass, field

from .ladders import CoolingLadder
from .power import PowerPlant


@dataclass
class Verdict:
    name: str
    family: str                 # "passive cooler", "active cooler", "generator"
    status: str                 # "kept", "dominated", "off the ladder", "never in a best plant", "replaceable"
    reason: str = ""
    penalty: int = 0            # most extra space needed at any tested load if this outfit is banned
    penalty_at: tuple = ()      # (energy, heat) where that happens
    used_at: list = field(default_factory=list)  # loads where it's in the best plant


def _base_name(name):
    return name.split(" + ")[0]


def _ease(name, availability):
    """Sort key: lower is harder to get, so it's tested for removal first."""
    a = availability[_base_name(name)]
    return (a.source == "sold", a.max_count is None)


def _dominates(a, b, better, availability):
    """`better` lists (attribute, sign) where sign +1 means higher is better."""
    if a.space > b.space:
        return False
    if b.max_count is None and a.max_count is not None:
        return False
    if b.max_count is not None and a.max_count is not None and a.max_count < b.max_count:
        return False
    if any(sign * (getattr(a, attr) - getattr(b, attr)) < -1e-9 for attr, sign in better):
        return False
    strictly = a.space < b.space or any(sign * (getattr(a, attr) - getattr(b, attr)) > 1e-9 for attr, sign in better)
    # Identical outfits: keep the easier one to get (or the first name).
    return strictly or _ease(a.name, availability) > _ease(b.name, availability) or (
        _ease(a.name, availability) == _ease(b.name, availability) and a.name < b.name)


def dumb_prune(items, better, availability, family, verdicts):
    kept = []
    for b in items:
        by = next((a for a in items if a is not b and _dominates(a, b, better, availability)), None)
        if by:
            verdicts[b.name] = Verdict(b.name, family, "dominated", f"by {by.name}")
        else:
            kept.append(b)
    return kept


def _plant_names(plant):
    return set(plant.generators) | set(plant.active)


def analyse(plant, availability, energies, heats):
    """Run all three passes on a full PowerPlant. Returns (verdicts, pruned PowerPlant)."""
    verdicts = {}
    grid = [(e, h) for e in energies for h in heats]

    # 1. Dumb dominance within each family. A passive cooler also dominates an active
    #    one that fits in no less space and removes no more heat even at full heat.
    passive = dumb_prune(plant.passive.coolers, [("cooling", 1)], availability, "passive cooler", verdicts)
    active = dumb_prune(plant.active_items, [("active", 1), ("cooling_energy", -1), ("passive", 1),
                                             ("consumption", -1)], availability, "active cooler", verdicts)
    for c in list(active):
        by = next((p for p in passive if p.space <= c.space and p.cooling >= c.active + c.passive), None)
        if by:
            verdicts[c.name] = Verdict(c.name, "active cooler", "dominated", f"by {by.name} (passive)")
            active.remove(c)
    gens = dumb_prune(plant.generator_items, [("energy", 1), ("heat", -1)], availability, "generator", verdicts)

    # 2. Passive coolers off the exact ladder.
    ladder = CoolingLadder(passive)
    on_ladder = ladder.used()
    for c in passive:
        if c.name not in on_ladder:
            verdicts[c.name] = Verdict(c.name, "passive cooler", "off the ladder",
                                       "some mix of other passive coolers always fits in no more space")
    ladder = CoolingLadder([c for c in passive if c.name in on_ladder])

    # 3. Smart: joint plant over the load grid.
    current = PowerPlant(ladder, gens, active, plant.max_generator_space, plant.max_active_space, plant.heat_fraction)
    base = {pt: current.solve(*pt) for pt in grid}
    best_space = {pt: p.space for pt, p in base.items() if p is not None}
    used = set().union(*(_plant_names(p) for p in base.values() if p is not None))
    families = {**{g.name: "generator" for g in gens}, **{c.name: "active cooler" for c in active}}
    unused = [n for n in families if n not in used]
    for n in unused:
        verdicts[n] = Verdict(n, families[n], "never in a best plant")
    current = current.without(unused)

    candidates = sorted(used, key=lambda n: (_ease(n, availability), -_space_of(current, n)))
    for name in candidates:
        trial = current.without([name])
        worst, worst_at, replaced_by = 0, (), Counter()
        for pt, space in best_space.items():
            p = trial.solve(*pt)
            extra = (p.space - space) if p is not None else 10 ** 6
            if extra > worst:
                worst, worst_at = extra, pt
            if p is not None and extra == 0 and name in _plant_names(base[pt]):
                replaced_by.update(_plant_names(p) - _plant_names(base[pt]))
        if worst == 0:
            alternatives = ", ".join(n for n, _ in replaced_by.most_common(3)) or "the other outfits"
            verdicts[name] = Verdict(name, families[name], "replaceable", f"ties with {alternatives}")
            current = trial
            base = {pt: current.solve(*pt) for pt in grid}
        else:
            verdicts[name] = Verdict(name, families[name], "kept", penalty=worst, penalty_at=worst_at)

    # Where each kept outfit is used, on the final plant.
    for pt, p in base.items():
        if p is not None:
            for n in _plant_names(p):
                verdicts[n].used_at.append(pt)
    for c in ladder.coolers:
        verdicts[c.name] = Verdict(c.name, "passive cooler", "kept")
    return verdicts, current


def _space_of(plant, name):
    for item in plant.generator_items + plant.active_items:
        if item.name == name:
            return item.space
    return 0
