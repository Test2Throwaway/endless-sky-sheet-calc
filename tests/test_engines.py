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
    # 2 space saved; the extra 0.4 energy and 1.5 heat per frame at 30% duty cost at most 0.72 + 0.27 space.
    assert run({"Old": steering(288, 12, .3, .6), "New": steering(420, 10, .7, 2.1)}) == {"Old": {"New": 1}}


def test_power_that_costs_more_than_the_space_saved_is_kept():
    assert run({"Old": steering(288, 12, .3, .6), "Hungry": steering(420, 11, 1.5, 2.1)}) == {}


def test_engine_capacity_and_classes_stay_strict():
    roomy = steering(420, 10, .3, .6)
    roomy["engine capacity"] = -13.
    assert run({"Old": steering(288, 12, .3, .6), "Roomy": roomy}) == {}
    burner = steering(420, 10, .3, .6, **{"afterburner thrust": 5.})
    assert run({"Old": steering(288, 12, .3, .6), "Burner": burner}) == {}


def test_whole_copies_count():
    assert run({"Big": steering(500, 20, 1., 1.), "Small": steering(260, 9, .4, .4)}) == {"Big": {"Small": 2}}
