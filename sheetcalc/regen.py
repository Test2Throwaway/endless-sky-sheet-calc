"""Regeneration passes: compensated dominance per solar case, like the engine pass (engines.py).

Shield generation, delayed shield generation and hull repair are compared by the strict rules (higher is better),
as are delays and every other stat, so an outfit that also does something else (energy storage, slots, links,
protection) is only beaten by one that does at least as much of it. Its outfit space, steady power (energy
generation and consumption, heat generation) and the energy and heat it uses while regenerating are traded at the
case's power plant rates.

How much of the time an outfit regenerates is not known, so a drop must hold at both 0% and 100% regeneration
duty; the cost is linear in the duty, so it then holds at every duty in between. Multipliers (shield energy,
shield generation, hull repair, hull energy) and multimodal armor have no direction, so outfits with them are only
ever beaten by an outfit with the same values.
"""

from .engines import FPS, STEADY_POWER, compensated_dominance, rate_box

REGEN_COSTS = {
    "shield energy": ("energy", FPS, "regen"),
    "shield heat": ("heat", FPS, "regen"),
    "delayed shield energy": ("energy", FPS, "regen"),
    "delayed shield heat": ("heat", FPS, "regen"),
    "hull energy": ("energy", FPS, "regen"),
    "hull heat": ("heat", FPS, "regen"),
}
TRADED = {**REGEN_COSTS, **STEADY_POWER}
REGEN = {"shield generation", "delayed shield generation", "hull repair rate", *REGEN_COSTS,
         "shield energy multiplier", "shield generation multiplier", "hull repair multiplier", "hull energy multiplier"}

def is_regen(candidate):
    return any(candidate.attrs.get(k) for k in REGEN)


def regen_dominance(outfits, availability, prices):
    """Return (regen outfits considered, {dropped outfit: {outfit that beats it: copies needed}})."""
    return compensated_dominance(outfits, availability, rate_box(prices, TRADED), TRADED, is_regen)
