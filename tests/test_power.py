import pytest

from sheetcalc.availability import Availability
from sheetcalc.ladders import CoolingLadder, Item
from sheetcalc.obsolescence import analyse
from sheetcalc.power import ActiveCooler, PowerPlant

DUCT = Item("Duct", 5, None, cooling=300)
SHUNT = Item("Shunt", 7, None, cooling=810)
BIG_SHUNT = Item("Big Shunt", 24, None, cooling=3240)
BAD_COOLER = Item("Bad Cooler", 10, None, cooling=720)  # strictly worse than Shunt

CELL = Item("Cell", 13, None, energy=168, heat=294)
REACTOR = Item("Reactor", 98, None, energy=1452, heat=2700)
# Not dominated (less heat than Reactor), but cells and Reactor always do better.
WEAK_REACTOR = Item("Weak Reactor", 100, None, energy=1092, heat=2400)
PANEL = Item("Panel", 2, None, energy=6)

MODULE = ActiveCooler("Module", 5, None, active=1260, cooling_energy=84)
GREEDY = ActiveCooler("Greedy Module", 5, None, active=1260, cooling_energy=200)  # same, but more energy


def test_cooling_ladder_is_exact_minimum_space():
    ladder = CoolingLadder([DUCT, SHUNT, BIG_SHUNT, BAD_COOLER])
    assert ladder.space_for(0) == 0
    assert ladder.space_for(300) == 5
    assert ladder.space_for(301) == 7
    assert ladder.space_for(1620) == 14   # 2 shunts beat a big shunt
    assert ladder.space_for(3240) == 24
    assert ladder.space_for(3241) == 29   # big shunt + duct
    assert "Bad Cooler" not in ladder.used()


def test_cooling_ladder_respects_copy_limits():
    unique = Item("Unique Shunt", 7, 1, cooling=810)
    ladder = CoolingLadder([unique, DUCT])
    assert ladder.space_for(810) == 7
    assert ladder.space_for(1110) == 12   # unique shunt + duct
    assert ladder.space_for(1620) == 22   # only one unique shunt, then ducts


def test_plant_covers_load_with_generators_and_cooling():
    plant = PowerPlant(CoolingLadder([SHUNT]), [CELL], [])
    p = plant.solve(100, 0)
    # One cell (13) gives 168 energy and 294 heat; one shunt (7) cools 810.
    assert (p.space, p.generator_space, p.passive_space) == (20, 13, 7)
    assert plant.solve(200, 0).space == 26 + 7  # two cells, 588 heat, still one shunt


def test_active_cooling_energy_comes_from_the_generators():
    # Needing 900 heat removed: passive would take two shunts (14). A module cools
    # 1260 × 0.75 = 945 at 75% heat and draws 84/1260 energy per heat removed.
    plant = PowerPlant(CoolingLadder([SHUNT]), [CELL], [MODULE], heat_fraction=.75)
    p = plant.solve(100, 900 - 294)
    assert p.active == {"Module": 1}
    assert p.active_heat == pytest.approx(900)
    assert p.active_energy == pytest.approx(900 * 84 / 1260)
    assert p.space == 13 + 5
    # With only 8 energy/s spare, the module can remove just 8 × 1260 / 84 = 120 heat/s,
    # so one shunt covers the other 780: 25 space, against 27 for passive alone.
    p = plant.solve(160, 900 - 294)
    assert (p.active, p.passive) == ({"Module": 1}, {"Shunt": 1})
    assert p.active_heat == pytest.approx(120)
    assert p.space == 13 + 5 + 7
    assert PowerPlant(CoolingLadder([SHUNT]), [CELL], []).solve(160, 900 - 294).space == 13 + 14


def test_obsolescence_passes():
    availability = {name: Availability("sold", None) for name in
                    ["Duct", "Shunt", "Big Shunt", "Bad Cooler", "Cell", "Reactor", "Weak Reactor", "Panel",
                     "Module", "Greedy Module", "Plunder Cell"]}
    availability["Plunder Cell"] = Availability("taken from ships only (plunder)", None)
    plunder_cell = Item("Plunder Cell", 13, None, energy=168, heat=294)  # identical to Cell, harder to get
    plant = PowerPlant(CoolingLadder([DUCT, SHUNT, BIG_SHUNT, BAD_COOLER]),
                       [CELL, plunder_cell, REACTOR, WEAK_REACTOR, PANEL], [MODULE, GREEDY])
    verdicts, pruned = analyse(plant, availability, energies=[0, 50, 150, 500, 1500], heats=[0, 500, 3000])
    assert verdicts["Bad Cooler"].status == "dominated"
    assert verdicts["Greedy Module"].status == "dominated"
    assert verdicts["Plunder Cell"].status == "dominated"   # identical stats: the sold one is kept
    assert verdicts["Cell"].status == "kept"
    assert verdicts["Weak Reactor"].status in ("never in a best plant", "replaceable")
    kept = {v.name for v in verdicts.values() if v.status == "kept"}
    assert {i.name for i in pruned.generator_items + pruned.active_items} <= kept
    # Pruning never changes the answer at the tested loads.
    for e in [0, 50, 150, 500, 1500]:
        for h in [0, 500, 3000]:
            assert pruned.solve(e, h).space == plant.solve(e, h).space
