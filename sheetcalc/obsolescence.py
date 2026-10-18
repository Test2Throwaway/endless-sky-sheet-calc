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

Only power and cooling stats are judged. An outfit can also matter for something
else (energy capacity, ion resistance, shield multipliers...). So pass 1 refuses to
call one outfit dominated by another if they differ on any other attribute, and the
later passes record those other stats on the verdict ("extras") so a caller can
decide whether "obsolete for power" is enough to drop it.
"""

from collections import Counter
from dataclasses import dataclass, field

from .ladders import CoolingLadder
from .power import PowerPlant
from .settings import ACTIVE_COOLING_HEAT_FRACTION


# Attributes the power plant model accounts for (or that only gate how many fit).
PLANT_ATTRIBUTES = {"outfit space", "energy generation", "energy consumption", "heat generation", "solar collection",
                    "solar heat", "cooling", "active cooling", "cooling energy", "solar cell", "reactor upgrades",
                    "anchor point", "unique"}
# Attributes that don't affect a ship's performance. Mass does, and is compared separately.
COSMETIC = {"category", "series", "index", "thumbnail", "description", "plural", "flotsam sprite", "flotsam chance",
            "linked", "cost", "unplunderable", "mass"}


def other_stats(name, outfits):
    """{attribute: value} an outfit (or slot combination) has beyond power and cooling."""
    if outfits is None:
        return {}
    parts = name.split(" + ")
    stats = {}
    for part in [parts[0]] + [p.split(" ", 1)[1].rstrip("s") if p[0].isdigit() else p for p in parts[1:]]:
        for key, value in outfits.get(part, outfits.get(part + "s", {})).items():
            if not key.startswith("_") and key not in PLANT_ATTRIBUTES and key not in COSMETIC:
                stats[key] = value
    return stats


@dataclass
class Verdict:
    name: str
    family: str                 # "passive cooler", "active cooler", "generator"
    status: str                 # "kept", "dominated", "off the ladder", "never in a best plant", "replaceable"
    reason: str = ""
    penalty: int = 0            # most extra space needed at any tested load if this outfit is banned
    penalty_at: tuple = ()      # (energy, heat) where that happens
    used_at: list = field(default_factory=list)  # loads where it's in the best plant
    extras: dict = field(default_factory=dict)   # stats beyond power and cooling


def _base_name(name):
    return name.split(" + ")[0]


def _ease(name, availability):
    """Sort key: lower is harder to get, so it's tested for removal first."""
    a = availability[_base_name(name)]
    return (a.source == "sold", a.max_count is None)


def _mass(name, outfits):
    return 0. if outfits is None else outfits.get(_base_name(name), {}).get("mass", 0.)


def _solar(name, outfits):
    return outfits is not None and outfits.get(_base_name(name), {}).get("solar collection", 0) > 0 or "Solar Cell" in name


def _dominates(a, b, better, availability, outfits=None):
    """`better` lists (attribute, sign) where sign +1 means higher is better. Outfits that
    differ on anything else, or where only one depends on sunlight, are never compared."""
    if a.space > b.space:
        return False
    if outfits is not None and (other_stats(a.name, outfits) != other_stats(b.name, outfits)
                                or _solar(a.name, outfits) != _solar(b.name, outfits)
                                or _mass(a.name, outfits) > _mass(b.name, outfits)):
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


def dumb_prune(items, better, availability, family, verdicts, outfits=None):
    kept = []
    for b in items:
        by = next((a for a in items if a is not b and _dominates(a, b, better, availability, outfits)), None)
        if by:
            verdicts[b.name] = Verdict(b.name, family, "dominated", f"by {by.name}")
        else:
            kept.append(b)
    return kept


def _plant_names(plant):
    return set(plant.generators) | set(plant.active)


def analyse(plant, availability, energies, heats, outfits=None):
    """Run all three passes on a full PowerPlant. `outfits` (the game data) lets the
    passes see stats beyond power and cooling. Returns (verdicts, pruned PowerPlant)."""
    return analyse_items(plant.passive.coolers, plant.generator_items, plant.active_items, availability, energies,
                         heats, outfits, plant.max_generator_space, plant.max_active_space, plant.heat_fraction)


def analyse_items(passive_items, generator_items, active_items, availability, energies, heats, outfits=None,
                  max_generator_space=400, max_active_space=48, heat_fraction=ACTIVE_COOLING_HEAT_FRACTION):
    """Like analyse(), from item lists. The joint plant is only built after the cheap
    passes have pruned the lists, which makes it much faster to build."""
    verdicts = {}
    grid = [(e, h) for e in energies for h in heats]

    # 1. Dumb dominance within each family. A passive cooler also dominates an active
    #    one that fits in no less space and removes no more heat even at full heat.
    passive = dumb_prune(passive_items, [("cooling", 1)], availability, "passive cooler", verdicts, outfits)
    active = dumb_prune(active_items, [("active", 1), ("cooling_energy", -1), ("passive", 1),
                                             ("consumption", -1)], availability, "active cooler", verdicts, outfits)
    for c in list(active):
        by = next((p for p in passive if p.space <= c.space and p.cooling >= c.active + c.passive
                   and other_stats(p.name, outfits) == other_stats(c.name, outfits)), None)
        if by:
            verdicts[c.name] = Verdict(c.name, "active cooler", "dominated", f"by {by.name} (passive)")
            active.remove(c)
    gens = dumb_prune(generator_items, [("energy", 1), ("heat", -1)], availability, "generator", verdicts,
                      outfits)

    # 2. Passive coolers off the exact ladder.
    ladder = CoolingLadder(passive)
    on_ladder = ladder.used()
    for c in passive:
        if c.name not in on_ladder:
            verdicts[c.name] = Verdict(c.name, "passive cooler", "off the ladder",
                                       "some mix of other passive coolers always fits in no more space")
    ladder = CoolingLadder([c for c in passive if c.name in on_ladder])

    # 3. Smart: joint plant over the load grid.
    current = PowerPlant(ladder, gens, active, max_generator_space, max_active_space, heat_fraction)
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
        worst, worst_at, replaced_by, resolved = 0, (), Counter(), {}
        # Only loads whose best plant uses this outfit can change: everywhere else that plant
        # is still allowed, and still the best. (Only zero-cost removals are ever committed,
        # so the current best plants are as small as the original ones.)
        for pt, plant in base.items():
            if plant is None or name not in _plant_names(plant):
                continue
            p = resolved[pt] = trial.solve(*pt)
            extra = (p.space - best_space[pt]) if p is not None else 10 ** 6
            if extra > worst:
                worst, worst_at = extra, pt
            if p is not None and extra == 0:
                replaced_by.update(_plant_names(p) - _plant_names(plant))
        if worst == 0:
            alternatives = ", ".join(n for n, _ in replaced_by.most_common(3)) or "the other outfits"
            verdicts[name] = Verdict(name, families[name], "replaceable", f"ties with {alternatives}")
            current = trial
            base.update(resolved)
        else:
            verdicts[name] = Verdict(name, families[name], "kept", penalty=worst, penalty_at=worst_at)

    # Where each kept outfit is used, on the final plant.
    for pt, p in base.items():
        if p is not None:
            for n in _plant_names(p):
                verdicts[n].used_at.append(pt)
    for c in ladder.coolers:
        verdicts[c.name] = Verdict(c.name, "passive cooler", "kept")
    for v in verdicts.values():
        v.extras = other_stats(v.name, outfits)
    return verdicts, current


def _space_of(plant, name):
    for item in plant.generator_items + plant.active_items:
        if item.name == name:
            return item.space
    return 0
