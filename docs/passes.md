# Obsolescence passes

The optimizer (`endless-sky-outfits-optimizer-unofficial`) searches over every outfit it may use. Most of them are
never part of a good design, and every one it can skip makes the search smaller. This tool works out, once per game
update, which outfits can be skipped *for a given kind of design*, and writes one pruned list per kind ("pass").
The optimizer picks the passes that match its request.

## Output shape

`reports/passes.json`:

```
{
  "settings": {...},                              # loads, solar cases, availability tiers used
  "passes": {
    "power/solar=median/availability=sold": {
      "options": {"solar": "median", "availability": "sold"},
      "kept":    {"generator": [...], "passive cooler": [...], "active cooler": [...]},
      "dropped": {"Blue Sun Reactor": {"family": ..., "status": ..., "reason": ..., "other stats": {...}}},
      "if banned": {"Large Reactor Module": 17}   # most extra space needed without it
    },
    ...
  },
  "robust": {"power/solar=median": {...}}         # see "Availability" below
}
```

A pass id is `family/axis=value/axis=value`. Families are pruned independently, so a request takes one pass per
family and unions the kept lists: e.g. `power/solar=none/...` + `weapons/lens=damage/...` + `engines/lens=all/...`.

## Families

Outfits fall into families that compete for the same job. Only outfits in the same family can make each other
obsolete; different families are linked only through the shared budgets (below).

| Family | Outfits | Status |
|---|---|---|
| power | generators, passive coolers, active coolers | **done**: exact whole-outfit search (`power.py`) |
| energy storage | batteries, capacitors (and generators' capacity) | planned: only matters for burst (combat) |
| engines | thrusters, steering, reversers, afterburners | planned |
| weapons | guns, turrets, secondary weapons + their ammo | planned |
| anti-missile | anti-missile turrets, optical lasing | planned |
| regeneration | shield generators, hull repair, relays, nanites, cortexes | planned |
| travel | drives, fuel tanks, ramscoops | planned |
| stealth and sensors | jammers, cloaks, scanners | planned: mostly unique stats, dominance only |
| capacity | cargo/outfit expansions, bunks, crew quarters | planned: dominance only |

These follow the legacy spreadsheet's tabs (Drives, Jammers, Scanners, Fuel, Generators, Batteries, Cooling,
Engines, Shields, Cargo & Outfit Expansions, Anti-Missile, the Utility Weapons tabs, Damage Weapons) and the
optimizer's metrics and tags.

## Axes

An axis is a design option that changes which outfits a family needs. Each family has its own axes; a family's
passes are every combination of *its* axes only.

| Family | Axis | Values | Optimizer option it serves |
|---|---|---|---|
| all | availability | sold, taken, all | the player's availability settings |
| power | solar | none, dim, median, bright, max | `must_run_dark`, `evader`, default, bright-star designs |
| weapons | lens | all, damage, shield damage, hull damage, disable, instantaneous, anti-missile, tractor, push, pull, slowing, ion, heat, shield disruption | `goal` (normal / disable / capture-intact / destroy), `[must] has`, `[may] bonus`, utility-weapon roles |
| weapons | mount | gun, turret | gun ports and turret mounts are separate capacities, so this is a split, not an axis |
| engines | lens | all, thrust, turn, reverse, no afterburner | maneuverability metrics, `reverse_thrust`, `hero` (no afterburner) |
| regeneration | lens | all, shields, hull | `durable` (shield regen, hull repair) |
| energy storage | fight | none, escort (90 s), dedicated (4 min) | `combat`, `fight` |

A **lens** names the stats that count. "X is obsolete under lens L" means: some other outfit (or whole-outfit
combination) is at least as good on every stat L counts, at no more cost on every shared budget. Lens `all` counts
every stat, so anything better at *anything* survives; narrower lenses prune more.

## Why families can run independently

Families interact only through the budgets they share: outfit space, weapon and engine capacity, gun ports and
turret mounts, mass, energy, heat and fuel. The power family is what turns energy and heat into outfit space, and
its plant search gives that exchange rate (`power_plant.md`). So every other family can be judged on a **true
cost**:

    cost = outfit space + energy/s × energy price + heat/s × heat price

The prices depend on the ship's size and the power pass (solar case), but only within a range. Each family is judged
against the whole range: since cost is linear in the prices, "A is no more expensive than B for every price in a
box" only needs checking at the box's corners. A verdict that holds at all corners holds for every power pass,
which is what makes the other families independent of the solar axis.

Budgets with no exchange rate (weapon capacity vs. outfit space, gun ports, mass) are compared as separate
dimensions, never traded.

The number of runs is therefore a **sum** over families, not a product over all axes:

| Family | Runs |
|---|---|
| power | 5 solar × 3 availability = 15 |
| weapons | 14 lenses × 3 availability = 42 |
| engines | 5 × 3 = 15 |
| regeneration | 3 × 3 = 9 |
| energy storage | 3 × 3 = 9 |

## Availability

The in-play list is already limited to what the player can get, but within it, some outfits are easy (sold) and
some need luck or a fight (plunder, capture, flotsam). A pass built from everything in play may drop a sold outfit
because a plunder-only one ties with it, which is wrong for a player who hasn't found that plunder yet. So:

- Each pass is run per tier: `sold` (outfitter only), `taken` (+ taken from ships), `all` (+ missions and events).
- The **robust** list for a case keeps an outfit if it is kept by the pass of *its own* tier. An outfit is dropped
  there only if outfits that are no harder to get always replace it, so the list stays valid for any player who can
  buy the sold outfits.

Licences and government-specific plunder are finer than these tiers; the optimizer's own availability filter still
applies on top.

## Things that need care

- **Whole outfits.** "Better per unit of space" is not dominance. Families where counts matter use an exact
  whole-outfit search (as power does) or check combinations, not ratios.
- **Stats outside the lens.** An outfit is never called dominated if it differs on a stat the pass doesn't model;
  such outfits are judged by the pass but flagged with their other stats, so a caller can keep them.
- **Pairs.** Launchers and their ammunition, reactors and overclockers, solar batteries and cells are judged as
  combinations.
- **Burst vs. steady.** The power pass is steady-state. Batteries, active cooling's real advantage and weapons' firing
  heat in combat belong to the energy storage family's fight axis.

## Efficiency

- Cheap passes first: strict dominance and the passive ladder shrink the lists before the expensive joint search is
  built, which is much faster than building it from everything.
- Passes are independent, so they run in parallel (`--jobs`, default all cores).
- Planned: cache each pass by a hash of its inputs (the outfits in its pool, the settings), so a game update only
  reruns the families whose outfits changed.
