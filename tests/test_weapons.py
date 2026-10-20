from sheetcalc.availability import Availability
from sheetcalc.weapons import damage_per_shot, lens_dominance, weapon_range

SOLD = Availability("sold", None)


def gun(**weapon):
    stats = {"reload": 10., "velocity": 10., "lifetime": 50., "shield damage": 10., "hull damage": 10.,
             "firing energy": 1., "firing heat": 1., **weapon}
    return {"category": "Guns", "outfit space": -10., "weapon capacity": -10., "gun ports": -1., "mass": 10.,
            "_weapon": stats}


def run(outfits, lens="damage"):
    return lens_dominance(outfits, {name: SOLD for name in outfits if "category" in outfits[name]}, lens)[1]


def test_damage_lens_ignores_effect_damage_and_hit_force():
    dropped = run({"Plain": gun(**{"shield damage": 12.}), "Ion": gun(**{"ion damage": 5., "hit force": 50.})})
    assert dropped == {"Ion": ["Plain"]}


def test_a_trade_off_is_kept():
    assert run({"Fast": gun(reload=5., **{"firing energy": 1.}), "Cheap": gun(**{"firing energy": .4})}) == {}


def test_costs_and_damage_are_per_second():
    # Twice the damage per shot at half the rate is the same damage per second, at lower energy per second.
    dropped = run({"Slow": gun(reload=20., **{"shield damage": 20., "hull damage": 20.}), "Fast": gun()})
    assert dropped == {"Fast": ["Slow"]}


def test_submunitions_count_80_percent_of_final_damage():
    outfits = {"Shell": gun(**{"shield damage": 100., "hull damage": 100., "submunition": [("Bit", 3.)]}),
               "Bit": {"_weapon": {"shield damage": 10., "hull damage": 5., "lifetime": 20.}}}
    weapon = outfits["Shell"]["_weapon"]
    assert damage_per_shot(outfits, weapon, "shield damage") == 24.
    assert weapon_range(outfits, weapon) == 10. * 70.


def test_range_override_and_medians():
    assert weapon_range({}, {"velocity": 10., "random velocity": 4., "lifetime": 10., "random lifetime": 2.}) == 132.
    assert weapon_range({}, {"velocity": 10., "lifetime": 10., "range override": 500.}) == 500.


def test_needing_ammunition_never_wins():
    dropped = run({"Launcher": gun(ammo=("Missile", 1.), **{"shield damage": 50.}), "Gun": gun()})
    assert dropped == {}


def test_anti_missile_lens_compares_only_anti_missile():
    def am(strength, reload):
        return {"category": "Turrets", "outfit space": -5., "weapon capacity": -5., "turret mounts": -1., "mass": 5.,
                "_weapon": {"anti-missile": strength, "reload": reload, "velocity": 200., "lifetime": 1.,
                            "firing energy": 5., "firing heat": 2.}}
    outfits = {"Good": am(10., 5.), "Weak": am(8., 5.), "Slow strong": am(20., 10.)}
    assert run(outfits, "anti-missile") == {"Weak": ["Good"]}
    assert run(outfits) == {}
