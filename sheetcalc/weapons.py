"""Weapon lenses: strict dominance on only the stats one kind of request cares about.

A lens drop is valid only for requests of that kind (see docs/tier-table.md for the stat choices):

- damage: regular fighting weapons for general-purpose combat roles. Weapons with shield or hull damage that
  aren't anti-missile or tractor beams. Effect damage, hit force, blast radius, tracking, penetration, dropoff
  and fire timing are ignored.
- anti-missile: anti-missile turrets, compared only with each other. Every combat ship wants some.

How the raw stats are abstracted:
- shots per second = 60 / reload; burst count and burst reload only bunch shots inside the cycle;
- damage and firing costs are per second;
- a weapon with submunitions always splits and 80% of its final submunitions hit (a splitting projectile deals
  nothing itself, Weapon::TotalDamage / Projectile.cpp);
- velocity and lifetime are medians (base + half the random part); velocity override and range override, where
  set, replace them as the game's AI and range display do (Weapon::WeightedVelocity, Weapon::Range).

Outfit-level attributes (space, mass, slots, ammo storage...) still use the strict rules, and availability tiers
and copy limits are respected the same way.
"""

from .attributes import PRESENCE, direction
from .strict import _candidates, _compare

FPS = 60.
SUBMUNITION_HIT_RATE = .8
DAMAGE_TYPES = ("shield damage", "hull damage")
DAMAGE_FIRING_COSTS = ("firing energy", "firing heat", "firing force", "firing fuel", "firing ion", "firing hull",
                       "relative firing shields")
ANTI_MISSILE_FIRING_COSTS = ("firing energy", "firing heat")


def shots_per_second(weapon):
    return FPS / max(1., weapon.get("reload", 1.))


def median_velocity(weapon):
    return weapon.get("velocity", 0.) + .5 * weapon.get("random velocity", 0.)


def _median_total_lifetime(outfits, weapon):
    children = [outfits.get(name, {}).get("_weapon", {}) for name, _ in weapon.get("submunition", [])]
    longest = max((_median_total_lifetime(outfits, c) for c in children), default=0.)
    return weapon.get("lifetime", 0.) + .5 * weapon.get("random lifetime", 0.) + longest


def weighted_velocity(weapon):
    return weapon.get("velocity override") or median_velocity(weapon)


def weapon_range(outfits, weapon):
    return weapon.get("range override") or weighted_velocity(weapon) * _median_total_lifetime(outfits, weapon)


def damage_per_shot(outfits, weapon, key):
    """Own damage, or 80% of the final submunitions' damage if the projectile splits."""
    if not weapon.get("submunition"):
        return weapon.get(key, 0.)
    return SUBMUNITION_HIT_RATE * _final_damage(outfits, weapon, key)


def _final_damage(outfits, weapon, key):
    if not weapon.get("submunition"):
        return weapon.get(key, 0.)
    return sum(count * _final_damage(outfits, outfits.get(name, {}).get("_weapon", {}), key)
               for name, count in weapon["submunition"])


def damage_stats(outfits, outfit):
    """{stat: (value, +1 higher is better / -1 lower)} for the damage lens, or None if not a fighting weapon."""
    weapon = outfit.get("_weapon")
    if not weapon or weapon.get("anti-missile") or weapon.get("tractor beam"):
        return None
    rate = shots_per_second(weapon)
    stats = {f"{key} /s": (damage_per_shot(outfits, weapon, key) * rate, 1) for key in DAMAGE_TYPES}
    if not any(v for v, _ in stats.values()):
        return None
    stats |= {f"{key} /s": (weapon.get(key, 0.) * rate, -1) for key in DAMAGE_FIRING_COSTS}
    stats |= {
        "velocity": (weighted_velocity(weapon), 1),
        "range": (weapon_range(outfits, weapon), 1),
        "inaccuracy": (weapon.get("inaccuracy", 0.), -1),
        "turn": (weapon.get("turn", 0.), 1),
        "homing": (1. if weapon.get("homing") else 0., 1),
        "missile strength": (weapon.get("missile strength", 0.), 1),
    }
    if outfit.get("category") == "Turrets":
        stats["turret turn"] = (weapon.get("turret turn") or 4., 1)
    if "ammo" in weapon:
        stats["ammo /s"] = (weapon["ammo"][1] * rate, -1)
    return stats


def anti_missile_stats(outfits, outfit):
    """{stat: (value, direction)} for the anti-missile lens, or None. Anti-missile turrets aim instantly
    (Hardpoint::FireSpecialSystem), so turret turn doesn't matter."""
    weapon = outfit.get("_weapon")
    if not weapon or not weapon.get("anti-missile"):
        return None
    rate = shots_per_second(weapon)
    stats = {"anti-missile": (weapon["anti-missile"], 1), "shots /s": (rate, 1),
             "range": (weapon_range(outfits, weapon), 1)}
    stats |= {f"{key} /s": (weapon.get(key, 0.) * rate, -1) for key in ANTI_MISSILE_FIRING_COSTS}
    if "ammo" in weapon:
        stats["ammo /s"] = (weapon["ammo"][1] * rate, -1)
    return stats


LENSES = {"damage": damage_stats, "anti-missile": anti_missile_stats}


def _lens_beats(b, a):
    """b's lens stats are at least as good as a's and strictly better somewhere (or tied: None)."""
    ammo_a, ammo_b = a["ammo"], b["ammo"]
    if ammo_b is not None and ammo_b != ammo_a:  # needing ammunition, or a different one, never wins
        return False
    strictly = ammo_b is None and ammo_a is not None
    for key in a["stats"].keys() | b["stats"].keys():
        d = (a["stats"].get(key) or b["stats"][key])[1]
        va, vb = a["stats"].get(key, (0., d))[0], b["stats"].get(key, (0., d))[0]
        if d * (vb - va) < -1e-9:
            return False
        strictly = strictly or d * (vb - va) > 1e-9
    return strictly or None


def lens_dominance(outfits, availability, lens):
    """Return (weapons in the lens, {dropped weapon: [weapons that beat it]})."""
    stats_of = LENSES[lens]
    entries = []
    for c in _candidates(outfits, availability):
        stats = stats_of(outfits, outfits[c.name])
        if stats is not None:
            ammo = outfits[c.name]["_weapon"].get("ammo")
            entries.append({"c": c, "stats": stats, "ammo": ammo[0] if ammo else None})
    dropped = {}
    for a in entries:
        beaters = []
        for b in entries:
            ca, cb = a["c"], b["c"]
            if b is a or cb.category != ca.category or cb.tier > ca.tier or cb.copy_limit < ca.copy_limit:
                continue
            top = _compare(ca.attrs, cb.attrs, direction, PRESENCE)
            if top is None:
                continue
            lens_result = _lens_beats(b, a)
            if lens_result is False:
                continue
            if top or lens_result or (cb.tier, -cb.copy_limit, cb.name) < (ca.tier, -ca.copy_limit, ca.name):
                beaters.append(cb.name)
        if beaters:
            dropped[a["c"].name] = sorted(beaters)
    return [e["c"].name for e in entries], dropped

