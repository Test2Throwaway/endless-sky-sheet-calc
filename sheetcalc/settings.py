"""Design parameters, carried over from the legacy sheet's "Magic Numbers" tab."""


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

# Reference ships for pricing, as (energy draw/s, heat/s) that the rest of the ship
# needs the power plant to cover. Rough guesses; adjust to the ships being designed.
REFERENCE_LOADS = {
    "light": (150, 800),
    "medium": (400, 2000),
    "heavy": (1000, 5000),
    "capital": (2500, 10000),
}

# Solar energy is counted at the median case; solar heat at the high (worst) case.
SOLAR_ENERGY_CASE = "median"
SOLAR_HEAT_CASE = "high"
