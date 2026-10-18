"""Design parameters, carried over from the legacy sheet's "Magic Numbers" tab."""


def solar_scale(distance):
    """Solar scale at a distance from a star (System::GetSolarGeneration)."""
    return .2 + 1.8 / (.001 * distance + 1)


# System solar power and ship distance from the star, per design case.
SOLAR_POWER = {"median": 1.1, "high": 1.86, "low": .7}
SOLAR_DISTANCE = {"median": 1400, "high": 800, "low": 2500}

SOLAR_MULTIPLIER = {case: SOLAR_POWER[case] * solar_scale(SOLAR_DISTANCE[case]) for case in SOLAR_POWER}

# Solar energy is counted at the median case; solar heat at the high (worst) case.
SOLAR_ENERGY_CASE = "median"
SOLAR_HEAT_CASE = "high"
