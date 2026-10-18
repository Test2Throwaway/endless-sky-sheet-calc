from sheetcalc import passes
from sheetcalc.availability import Availability
from sheetcalc.settings import SOLAR_SCENARIOS

SOLD, TAKEN = Availability("sold", None), Availability("taken from ships only (plunder, capture)", None)

# Per-frame values, as in the game data.
OUTFITS = {
    "Shunt": {"category": "Systems", "outfit space": -7., "cooling": 13.5},
    "Panel": {"category": "Power", "outfit space": -2., "solar collection": .1},
    "Cell": {"category": "Power", "outfit space": -13., "energy generation": 2.8, "heat generation": 4.9},
    "Plunder Cell": {"category": "Power", "outfit space": -13., "energy generation": 2.8, "heat generation": 4.9},
}
AVAILABILITY = {"Shunt": SOLD, "Panel": SOLD, "Cell": SOLD, "Plunder Cell": TAKEN}


def test_tiers_and_pools():
    assert passes.tier_of(SOLD) == "sold"
    assert passes.tier_of(TAKEN) == "taken"
    assert passes.tier_of(Availability("mission or event only", 1)) == "all"
    assert set(passes.pool(AVAILABILITY, "sold")) == {"Shunt", "Panel", "Cell"}
    assert set(passes.pool(AVAILABILITY, "all")) == set(AVAILABILITY)


def _run(solar, tier):
    passes._init_worker(OUTFITS, AVAILABILITY)
    return passes.run_power_pass(solar, tier, energies=[0, 5, 100, 300], heats=[0, 500])[1]


def test_solar_axis_changes_what_is_kept():
    assert "Panel" in _run("median", "sold")["kept"]["generator"]
    none = _run("none", "sold")
    assert "Panel" not in none["kept"]["generator"]
    assert none["dropped"]["Panel"]["status"] == "never in a best plant"


def test_robust_list_keeps_sold_outfit_that_only_ties_with_plunder():
    results = {passes.pass_id("median", t): _run("median", t) for t in passes.TIERS}
    # With everything allowed, the identical sold and plunder cells tie; the sold one wins the tie.
    assert "Cell" in results[passes.pass_id("median", "all")]["kept"]["generator"]
    robust = passes.robust_kept(results, AVAILABILITY, "median")
    assert "Cell" in robust["generator"]
    assert "Plunder Cell" not in robust["generator"]


def test_scenarios_follow_the_game_formula():
    assert SOLAR_SCENARIOS["none"].solar_energy == 0
    assert SOLAR_SCENARIOS["median"].solar_energy < SOLAR_SCENARIOS["bright"].solar_energy < SOLAR_SCENARIOS["max"].solar_energy
    # Legacy convention: the median case counts heat as if in bright sunlight.
    assert SOLAR_SCENARIOS["median"].solar_heat == SOLAR_SCENARIOS["bright"].solar_heat


def test_price_envelope_spans_every_pass():
    results = {passes.pass_id(s, "sold"): _run(s, "sold") for s in ("none", "max")}
    env = passes.price_envelope(results)
    every = [p for r in results.values() for p in r["prices"].values()]
    assert env["energy"] == [min(p["energy"] for p in every), max(p["energy"] for p in every)]
    assert env["energy"][0] > 0
