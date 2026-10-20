from sheetcalc.availability import Availability
from sheetcalc.strict import strict_dominance

SOLD = Availability("sold", None)
TAKEN = Availability("taken from ships only (plunder, capture)", None)


def engine(thrust, space, energy=1., heat=1., mass=None, **extra):
    return {"category": "Engines", "outfit space": -space, "engine capacity": -space, "mass": space if mass is None else mass,
            "thrust": thrust, "thrusting energy": energy, "thrusting heat": heat, "cost": 1000., **extra}


def run(outfits, availability=None):
    availability = availability or {name: SOLD for name in outfits}
    return strict_dominance(outfits, availability)[1]


def test_better_in_every_way_wins_and_cost_is_ignored():
    dropped = run({"Good": engine(20, 10, cost=9e9), "Bad": engine(15, 10)})
    assert dropped == {"Bad": {"Good": 1}}


def test_a_trade_off_is_not_dominance():
    assert run({"Strong": engine(20, 12), "Small": engine(15, 10)}) == {}


def test_whole_copies_of_a_small_outfit_can_beat_a_big_one():
    dropped = run({"Small": engine(10, 5, .5, .5), "Big": engine(18, 11, 1., 1.)})
    assert dropped == {"Big": {"Small": 2}}


def test_unknown_or_unequal_attributes_block():
    assert run({"Good": engine(20, 10), "Odd": engine(15, 10, **{"shield generation multiplier": .2})}) == {}


def test_presence_tags_block_both_ways():
    with_afterburner = engine(20, 10, **{"afterburner thrust": 5.})
    assert run({"Burner": with_afterburner, "Plain": engine(15, 10)}) == {}


def test_harder_to_get_never_beats_easier():
    outfits = {"Plunder": engine(20, 10), "Shop": engine(15, 10)}
    assert run(outfits, {"Plunder": TAKEN, "Shop": SOLD}) == {}
    assert run(outfits, {"Plunder": SOLD, "Shop": TAKEN}) == {"Shop": {"Plunder": 1}}


def test_copy_limited_never_beats_unlimited():
    outfits = {"Unique": engine(20, 10), "Common": engine(15, 10)}
    assert run(outfits, {"Unique": Availability("sold", 1), "Common": SOLD}) == {}


def test_identity_outfits_are_never_dropped():
    outfits = {"Brig": {"category": "Systems", "outfit space": -3., "mass": 3.},
               "Scanner": {"category": "Systems", "outfit space": -1., "mass": 1., "cargo scan power": 9.}}
    assert run(outfits) == {}


def test_weapons_compare_derived_keys_and_turret_default():
    def turret(damage, **weapon):
        return {"category": "Turrets", "outfit space": -10., "weapon capacity": -10., "turret mounts": -1.,
                "mass": 10., "_weapon": {"reload": 10., "velocity": 10., "lifetime": 50., "hull damage": damage,
                                         "shield damage": damage, **weapon}}
    # Absent turret turn on a turret means the game's 240°/s (4 per frame), so 3 per frame is worse.
    dropped = run({"Fast": turret(10.), "Slow": turret(10., **{"turret turn": 3.})})
    assert dropped == {"Slow": {"Fast": 1}}
    # Effect damage is a class: a plain weapon never beats one with ion damage.
    assert run({"Plain": turret(20.), "Ion": turret(10., **{"ion damage": 5.})}) == {}
