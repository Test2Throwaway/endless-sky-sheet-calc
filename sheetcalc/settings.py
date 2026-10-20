"""Design parameters, carried over from the legacy sheet's "Magic Numbers" tab.

Module-level values are defaults. Code that depends on them takes a `Scenario` (or explicit
arguments) so that passes with different settings can run side by side.
"""

from dataclasses import dataclass


def solar_scale(distance):
    """Solar scale at a distance from a star (System::GetSolarGeneration)."""
    return .2 + 1.8 / (.001 * distance + 1)


# System solar power and ship distance from the star, per design case.
SOLAR_POWER = {"median": 1.1, "high": 1.86, "low": .7}
SOLAR_DISTANCE = {"median": 1400, "high": 800, "low": 2500}

SOLAR_MULTIPLIER = {case: SOLAR_POWER[case] * solar_scale(SOLAR_DISTANCE[case]) for case in SOLAR_POWER}

# Active coolers work in proportion to how hot the ship is: at heat fraction f they
# remove f × their active cooling, using f × their cooling energy. A ship overheats
# above 100% heat and recovers below 90%, so a design should only count on active
# cooling up to some comfortable heat fraction.
ACTIVE_COOLING_HEAT_FRACTION = .75

# The brightest star in the game is an O supergiant (power 5.2, data/stars.txt); 400 is a close orbit.
MAX_SOLAR_POWER, MAX_SOLAR_DISTANCE = 5.2, 400


@dataclass(frozen=True)
class Scenario:
    """The conditions a power plant is designed for."""
    name: str
    solar_energy: float  # multiplier on solar collection
    solar_heat: float    # multiplier on solar heat
    heat_fraction: float = ACTIVE_COOLING_HEAT_FRACTION


def _solar_scenarios():
    """The pruner's solar cases. The middle three are the optimizer's own constants (calculator.py), so a
    design routed to a case is checked against the same light it will be judged in."""
    brightest = MAX_SOLAR_POWER * solar_scale(MAX_SOLAR_DISTANCE)
    stay = 1.70 * 1.229    # optimizer SOLAR_STAY: 75th-percentile star at 750 (the bright-star check)
    return {
        # No star, or a ship that must run dark: solar outfits give nothing.
        "dark": Scenario("dark", 0., 0.),
        # Optimizer SOLAR_EVADING: 20th-percentile star at 5000.
        "evader": Scenario("evader", .70 * .50, stay),
        # Optimizer SOLAR_COMBAT: 30th-percentile star at 3000; heat at the bright-star check, so a design
        # never overheats when it visits a bright system.
        "normal": Scenario("normal", .76 * .65, stay),
        # Designed to stay near bright stars.
        "bright": Scenario("bright", stay, stay),
        # Close to the brightest star in the game: the most solar can ever do.
        "max": Scenario("max", brightest, brightest),
    }


# Reference ships for pricing, as (energy draw/s, heat/s) that the rest of the ship
# needs the power plant to cover. Rough guesses; adjust to the ships being designed.
REFERENCE_LOADS = {
    "light": (150, 800),
    "medium": (400, 2000),
    "heavy": (1000, 5000),
    "capital": (2500, 10000),
}

# Ship loads (energy draw/s, heat/s from everything but the power plant) over which
# smart obsolescence is judged. Denser at the small end, where whole outfits make
# the biggest steps.
OBSOLESCENCE_ENERGY = [0, 10, 20, 35, 50, 75, 100, 130, 160, 200, 250, 300, 375, 450, 550, 650, 800,
                       950, 1100, 1300, 1500, 1750, 2000, 2400, 2800, 3300, 3800]
OBSOLESCENCE_HEAT = [0, 100, 250, 500, 750, 1000, 1500, 2000, 2500, 3000, 4000, 5000, 6500, 8000,
                     10000, 12500, 15000]

# Solar energy is counted at the median case; solar heat at the high (worst) case.
SOLAR_ENERGY_CASE = "median"
SOLAR_HEAT_CASE = "high"

SOLAR_SCENARIOS = _solar_scenarios()
# The legacy sheet's design case, used by the ladder and plant reports: typical sunlight for energy,
# bright sunlight for heat.
DEFAULT_SCENARIO = Scenario("median", SOLAR_MULTIPLIER["median"], SOLAR_MULTIPLIER["high"])
