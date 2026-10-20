"""How strict dominance compares each attribute. See docs/tier-table.md for the reasoning.

Every attribute is one of:
- HIGHER or LOWER: a better outfit may differ in that direction;
- PRESENCE: also HIGHER or LOWER, but having it at all (non-zero) is a class: a request can forbid it, or it
  is a different kind of outfit, so an outfit with it never beats one without it, or the reverse;
- COSMETIC: ignored;
- anything else: must be equal. Unknown and incomparable attributes (multipliers, special mechanics) therefore
  never let one outfit beat another unless both have the same value.

Values are as stored in the game data (per frame where the game uses frames). Capacities are negative when used,
so "less used" is "higher".
"""

COSMETIC = {
    "_file", "thumbnail", "description", "series", "index", "plural", "display name", "flare sprite", "flare sound",
    "steering flare sprite", "steering flare sound", "reverse flare sprite", "reverse flare sound",
    "afterburner effect", "flotsam sprite", "flotsam chance", "jump effect", "can jettison", "unplunderable",
    "licenses",
    # The optimizer never scores price (it only prints it), so strict dominance ignores it. A credit-capped
    # design would need it back; see docs/pruner-design.md.
    "cost",
}

HIGHER = {
    # Capacities and slots (negative = used).
    "outfit space", "cargo space", "weapon capacity", "engine capacity", "gun ports", "turret mounts",
    "reactor upgrades", "relay upgrades", "nanite upgrades", "solar cell", "shield connection point",
    "anchor point", "spinal mount", "multimodal armor", "asteroid mount small", "asteroid mount jd", "lasing power",
    # Power and cooling.
    "energy generation", "energy capacity", "solar collection", "cooling", "active cooling", "heat dissipation",
    "heat capacity",
    # Movement.
    "thrust", "turn", "reverse thrust", "afterburner thrust", "drag reduction", "inertia reduction",
    # Regeneration.
    "shield generation", "hull repair rate", "delayed shield generation",
    # Fuel and travel.
    "fuel capacity", "fuel generation", "ramscoop", "jump range", "jump speed",
    # Systems.
    "bunks", "crew equivalent", "tactical scan power", "asteroid scan power", "cargo scan power",
    "cargo scan efficiency", "outfit scan power", "outfit scan efficiency", "atmosphere scan", "radar jamming",
    "optical jamming", "scan interference", "cargo scan opacity", "outfit scan opacity",
    "holographic entertainment", "capture attack", "capture defense",
}

LOWER = {
    "mass", "required crew",
    "heat generation", "energy consumption", "solar heat", "cooling energy",
    "thrusting energy", "thrusting heat", "thrusting fuel", "turning energy", "turning heat",
    "reverse thrusting energy", "reverse thrusting heat", "afterburner energy", "afterburner heat",
    "afterburner fuel", "afterburner shields",
    "shield energy", "shield heat", "shield fuel", "hull energy", "hull heat", "delayed shield energy",
    "delayed shield heat", "shield delay", "depleted shield delay",
    "jump fuel", "drag", "overheat damage rate", "scan brightness", "operating costs",
}

# Attributes that only say how much room an outfit takes. An outfit with nothing but these has no
# performance to compare: its value is its identity (missions ask for a Brig or Luxury Accommodations by
# name), so it is never dropped.
FOOTPRINT = {"outfit space", "cargo space", "weapon capacity", "engine capacity", "mass", "required crew"}

# Every "<x> protection" and "<x> resistance" is higher-is-better; every "<x> capacity" not listed above is
# ammunition storage, higher-is-better (a launcher provides it, ammunition uses it).
HIGHER_SUFFIXES = (" protection", " resistance", " capacity")

# Having these at all is a class (see the module docstring).
PRESENCE = {
    "solar collection", "ramscoop", "afterburner thrust", "thrusting fuel", "capture attack", "capture defense",
    "cloak", "illegal", "atrocity", "automaton", "hyperdrive", "jump drive", "scram drive", "quantum keystone",
    "bunks",
}

WEAPON_COSMETIC = {
    "sprite", "hardpoint sprite", "hardpoint offset", "sound", "empty sound", "icon", "fire effect", "live effect",
    "hit effect", "target effect", "die effect", "fade out",
}

WEAPON_HIGHER = {
    "shield damage", "hull damage", "heat damage", "ion damage", "scrambling damage", "slowing damage",
    "disruption damage", "discharge damage", "corrosion damage", "leak damage", "burn damage", "energy damage",
    "fuel damage", "minable damage", "prospecting", "anti-missile", "tractor beam",
    "velocity", "lifetime", "range override", "velocity override", "turret turn",
}

WEAPON_LOWER = {
    "reload", "firing energy", "firing heat", "firing fuel", "firing hull", "firing shields", "firing ion",
    "relative firing shields", "inaccuracy",
}

# Effects, utility and costs a request can single out: a weapon with one never beats a weapon without it.
WEAPON_PRESENCE = {
    "heat damage", "ion damage", "scrambling damage", "slowing damage", "disruption damage", "discharge damage",
    "corrosion damage", "leak damage", "burn damage", "energy damage", "fuel damage", "minable damage",
    "prospecting", "anti-missile", "tractor beam", "firing fuel", "firing hull", "firing shields", "firing ion",
    "relative firing shields",
}

# The game's values for fields that are not 0 when absent.
WEAPON_DEFAULTS = {"reload": 1.}
TURRET_TURN_DEFAULT = 4.  # per frame (240°/s) for turrets that aren't anti-missile or tractor beams


def direction(attribute):
    """+1 (higher is better), -1 (lower is better), 0 (ignored) or None (must be equal)."""
    if attribute in COSMETIC:
        return 0
    if attribute in HIGHER or attribute.endswith(HIGHER_SUFFIXES):
        return 1
    if attribute in LOWER:
        return -1
    return None


def weapon_direction(key):
    if key in WEAPON_COSMETIC:
        return 0
    if key in WEAPON_HIGHER:
        return 1
    if key in WEAPON_LOWER:
        return -1
    return None
