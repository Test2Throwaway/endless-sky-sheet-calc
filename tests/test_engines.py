from sheetcalc.availability import Availability
from sheetcalc.engines import engine_dominance, rate_box

SOLD = Availability("sold", None)
PRICES = {"light": {"energy": .1, "heat": .005}, "heavy": {"energy": .05, "heat": .01}}


def steering(turn, space, energy, heat, **extra):
    return {"category": "Engines", "outfit space": -space, "engine capacity": -space, "mass": space,
            "turn": turn, "turning energy": energy, "turning heat": heat, **extra}


def run(outfits):
    return engine_dominance(outfits, {n: SOLD for n in outfits}, rate_box(PRICES))[1]


def test_saved_space_pays_for_extra_power():
    # 4 space saved; the extra 0.4 energy and 1.5 heat per frame at 100% duty cost at most 2.4 + 0.9 space.
    assert run({"Old": steering(288, 12, .3, .6), "New": steering(420, 8, .7, 2.1)}) == {"Old": {"New": 1}}


def test_power_that_costs_more_than_the_space_saved_is_kept():
    assert run({"Old": steering(288, 12, .3, .6), "Hungry": steering(420, 10, .7, 2.1)}) == {}


def test_engine_capacity_and_classes_stay_strict():
    roomy = steering(420, 10, .3, .6)
    roomy["engine capacity"] = -13.
    assert run({"Old": steering(288, 12, .3, .6), "Roomy": roomy}) == {}
    burner = steering(420, 10, .3, .6, **{"afterburner thrust": 5.})
    assert run({"Old": steering(288, 12, .3, .6), "Burner": burner}) == {}


def test_whole_copies_count():
    assert run({"Big": steering(500, 20, 1., 1.), "Small": steering(260, 9, .4, .4)}) == {"Big": {"Small": 2}}


def test_regen_needs_other_stats_matched_and_holds_at_both_duties():
    from sheetcalc.regen import regen_dominance

    def gen(regen, space, energy, **extra):
        return {"category": "Systems", "outfit space": -space, "mass": space, "shield generation": regen,
                "shield energy": energy, **extra}

    def regen_run(outfits):
        return regen_dominance(outfits, {n: SOLD for n in outfits}, PRICES)[1]

    assert regen_run({"Old": gen(.2, 15, .2), "New": gen(.28, 11, .28)}) == {"Old": {"New": 1}}
    # Storage is another stat: only an outfit with at least as much storage can beat it.
    assert regen_run({"Core": gen(.2, 15, .2, **{"energy capacity": 1000.}), "New": gen(.28, 11, .28)}) == {}
    # Much hungrier: cheaper at 0% duty, dearer at 100%, so kept.
    assert regen_run({"Old": gen(.2, 15, .2), "Hungry": gen(.28, 14, 1.)}) == {}
