# Pruner design (paper draft)

The pruner works out, once per game update, which outfits the optimizer can safely skip for a given kind of design.
It writes its results as **relations** ("A is beaten by B under these conditions"), and the optimizer applies them to
each request. This document is the full design; nothing beyond the power passes is built yet.

Background: `docs/passes.md` (families and independence), `docs/scenario-brainstorm.md` (about 190 design scenarios,
the attribute directions and zero-value rulings, worked out with the optimizer session).

## 1. Principles

1. **The pruner aids the optimizer; it does not replace it.** It only removes outfits that cannot help, so the
   optimizer searches a smaller space. Anything that needs judgement about the build stays in the pool.
2. **Never wrong, sometimes timid.** Every drop must be valid for every request routed to that pass. When in doubt,
   keep. A pruned list that misses a good outfit is a bug; one that keeps a useless outfit only costs search time.
3. **Credits only for universally relevant stats.** A stat is converted into outfit space only if every build that
   uses the family pays for or uses it. Conditional stats only protect outfits; situational stats keep them.
4. **Unknown means keep.** An attribute, flag or mechanic the pruner doesn't classify blocks pruning of that outfit
   and is reported, so it can be classified after a game update.
5. **Relations, not lists.** Results say what beats what, under which conditions and from which availability, so the
   optimizer can apply them to any user's availability settings.
6. **Pre-run the common, compute the rare on first request, cache both.** No game data in the optimizer repo:
   everything is generated on the user's machine at import time or on first request.

## 2. Inputs and outputs

**Inputs**
- Game data (outfits, with weapon sub-blocks, ammo links and slot attributes).
- The optimizer's availability model, used only to tag each outfit's availability tier and copy limit. A user's
  actual availability is applied later, when relations are used.
- Settings: the solar cases, standard combat cases and load grids below.

**Output: one relation store per game data hash and pruner version**

```
{
  "version": ..., "game data hash": ..., "settings": {...},
  "passes": {
    "<pass id>": {
      "family": "engines",
      "conditions": {"solar": "normal"},
      "front size": 12,
      "relations": {
        "<dropped outfit>": {
          "beaten by": ["<outfit>"] | [{"<outfit>": count, ...}],   # one outfit, or a whole-outfit combination
          "rule": "strict" | "compensated" | "ladder" | "plant",
          "replacement tier": "sold" | "taken" | "all",
          "reason": "..."
        }
      },
      "kept": {"<outfit>": {"why": "front" | "unknown attribute X" | "situational stat Y" | ...}},
      "rates": {...}                                              # power passes only (section 5)
    }
  },
  "blocked by unknown attributes": {"<attribute>": ["<outfit>", ...]}
}
```

A pass id is `family/condition=value/...`, e.g. `weapons/solar=normal/case=nimble-240`.

## 3. Attribute model

Before any comparison, every outfit is turned into a normalised vector. Each attribute is classified exactly once,
in a table kept with the code; the table is the main thing to review after a game update.

### 3.1 Effective values

Raw fields are converted before comparing (details in `scenario-brainstorm.md`):

- **Defaults, not 0:** reload, burst reload and burst count (1); ammo usage (1); turret turn 0 on a turret that is not
  anti-missile or tractor (240°/s); jump fuel ≤ 0 (100 / 150 / 200 by drive); jump range 0 (system default);
  disabled and minable damage absent (= hull damage); threshold percentage 0 (size formula); multipliers (1 + value).
- **Infinitely good at 0 or absent:** no ammo (unlimited magazine), projectile drag 0, arc absent (360°), no damage
  dropoff, penetration count 0 (unlimited), zero firing or upkeep costs, zero delays.
- **Derived values:** shots per second; range (range override, else velocity × total lifetime with submunitions);
  damage per second by type; instantaneous weapons count as infinitely fast.
- **Count-capped values:** capture attack and defense count only up to the crew that can use them.

### 3.2 Direction

Every value is **higher is better**, **lower is better**, or **blocked** (see the direction table in
`scenario-brainstorm.md`). Capacities used (outfit, engine, weapon space, gun ports, turret mounts, special slots)
are always lower is better and never convert into each other.

### 3.3 Relevance tiers

Tiers are per family: a stat can be universal within one family and conditional in another.

| Tier | Meaning | Treatment | Examples |
|---|---|---|---|
| **1 Universal** | every build that uses the family pays for or uses it | converted into outfit space with the power case's rates (section 5); prunes | outfit space, mass, energy generation and consumption, heat generation, passive cooling; thrusting and turning energy and heat at cruise duty (engines); firing energy and heat at combat duty (weapons, combat cases only) |
| **2 Conditional** | relevant to many builds, not all | a plain dimension: an outfit with more is never dropped by one with less; never converted, never a credit | energy capacity, fuel capacity, fuel generation and use, ramscoop, cargo space, protections, resistances, jamming, afterburner and reverse stats, active cooling |
| **3 Situational** | relevant only when a role asks for it | the outfit is never pruned, except by strict dominance against an outfit that matches the stat exactly | scanning, bunks, capture attack and defense, cloak, gaslining, drag reduction, magnetic nozzle, multipliers, special mechanics (inductive extraction, delayed shield generation, overheat damage), anything unknown |

Active cooling is tier 2, not tier 1: it only works when the ship is hot, and whether that's acceptable is a design
choice. The power plant search uses it, but other families are never credited for it.

### 3.4 Class keys

Outfits are only compared within the same value of every class key:

- **Category and slot:** guns, turrets, secondary weapons, engines, systems; special slots (spinal mount, anchor
  points, bay types).
- **Presence tags** (a request can forbid them, so a tagged outfit never beats an untagged one): afterburner, cloak,
  illegal, solar, ramscoop, torch, missile, fuel weapon, anti-missile, jump drive, hyperdrive, scram drive, damage
  weapon, instantaneous, shield disruption, push weapon, pull weapon, tractor beam.
- **Weapon mechanics:** ammo-free or which ammo; missile or not; homing; blast and safe; damage dropoff; phasing,
  gravitational, fused, parallel, stream, cluster, no-collision flags.
- **Copy limit:** a copy-limited outfit never beats an unlimited one.
- **Effect vector (weapons):** the set of damage types a weapon deals beyond shield and hull. A plain damage weapon
  never beats an effect weapon, and effect weapons only beat ones with the same effect set.

### 3.5 Fit and combinations

- **Fit before dominance:** A may only beat B if A uses no more of every capacity B uses, so A fits wherever B fits.
- **Whole outfits:** a combination (k × A, or A + C) may beat B only through an exact whole-outfit search (ladders,
  the power plant). Ratios ("better per space") are never dominance.
- **Pairs as units:** launcher + its ammo + racks (at the case's fights per restock); reactor + overclockers; solar
  battery + cells; torch + remass injector.

## 4. Layer 0: strict dominance (at import, every family)

The user's first priority. It needs no prices, no cases and no lenses, so it is valid for every request and runs once.

A is dropped in favour of B if all of these hold:
1. Same class keys (3.4) and B fits wherever A fits (3.5).
2. B is at least as good as A on every effective value with a direction, in every tier, and strictly better on one.
   Mass and cost count (lower is better). The strict mass option (a lighter B only wins if it also has at least A's
   heat capacity) is on by default.
3. Neither outfit has a blocked or unknown attribute.
4. B is no harder to get than A (availability tier) and no more copy-limited.

Identical outfits: keep the easier one to get, then the first by name.

## 5. Exchange rates (from the power layer)

Each power pass produces rates in outfit space per unit, for tier 1 stats only:

- **energy:** space per energy/s, from the joint power plant search;
- **heat:** space per heat/s, from the same search (the passive cooling ladder plus the generators' own heat);
- the range of each rate over ship sizes (the reference loads), as a box.

A **compensated cost** is `space + Σ(tier-1 stat × rate)`. Activity stats are weighted by the optimizer's duty
cycles: thrust 70% and turn 30% at cruise for engines; primaries 100% and secondaries 80% over the case's fight for
weapons. A compensated drop needs B's cost ≤ A's cost **at every corner of the rate box**; cost is linear in the
rates, so the corners are enough.

## 6. Families and the pass chain

Energy and heat are the only shared resources with an exchange rate, so families depend on power only through the
rates. Each family therefore multiplies by the 5 solar cases and nothing else, except weapons.

| Order | Family | Method | Conditions | Pre-run passes |
|---|---|---|---|---|
| 0 | All families | strict dominance | none | 1 |
| 1 | Power and cooling (generators, passive and active coolers) | joint whole-outfit plant search over a load grid; produces the rates | solar (5) | 5 |
| 2 | Energy storage (batteries, capacitors) | capacity ladder; generators with storage kept by their storage dimension | none | 1 |
| 2 | Fuel and travel (tanks, ramscoops, fuel generation, drives) | compensated dominance; drives are class keys | solar (5) | 5 |
| 2 | Engines (thrusters, steering, reversers; afterburners and torches as classes) | compensated dominance on thrust, turn, reverse | solar (5) | 5 |
| 2 | Regeneration (shield generators, hull repair; relays, nanites, cortexes as combinations) | compensated dominance on shield regen and hull repair, protections as dimensions | solar (5) | 5 |
| 2 | Anti-missile | compensated dominance on anti-missile strength, rate, range | solar (5) | 5 |
| 2 | Systems (cargo, bunks, scanners, jammers, capture, expansions) | strict dominance only (layer 0) | none | 0 |
| 3 | Standard combat weapons | compensated dominance within the case | solar (5) × combat case (6) | 30 |

**Total pre-run: 57 passes**, per game update, on the user's machine. At today's speeds (power passes take
20 s–3 min; the others should be seconds, being dominance rather than search) that is a few minutes on 12 cores.

### 6.1 Solar cases (5)

The optimizer checks every design against fixed solar conditions; the pruner's cases match them and extend them:

| Case | Solar energy × | Solar heat × | Source |
|---|---|---|---|
| dark | 0 | 0 | `must_run_dark`, black holes |
| evader | 0.35 | 2.09 | optimizer `SOLAR_EVADING` (dim star at 5000); heat at `SOLAR_STAY` |
| normal | 0.49 | 2.09 | optimizer `SOLAR_COMBAT` (30th-percentile star at 3000); heat at `SOLAR_STAY` |
| bright | 2.09 | 2.09 | optimizer `SOLAR_STAY` (75th-percentile star at 750), as a design point |
| max | 7.7 | 7.7 | brightest star in the game (O supergiant, power 5.2) at a close 400 |

A design routed to a solar case is designed for that light. Heat is always taken at least at the bright level,
except in dark, so a design never overheats when it visits a bright system.

### 6.2 Standard combat weapon cases (6)

Within a weapon category, the optimizer's weapon value is reordered only by the hull's agility (through the
comfortable range) and by the fight length (magazine window, secondary duty, ammo depth, how long sustain runs).
Fire rate, turret turn and projectile speed are fixed per weapon for every combat role.

| Case | Agility | Engagement | Goal | Status |
|---|---|---|---|---|
| slow-90 | slow (< 110) | escort, 90 s | normal | standard |
| slow-240 | slow | dedicated, 240 s | normal | standard |
| nimble-90 | nimble (≥ 110) | escort, 90 s | normal | standard |
| nimble-240 | nimble | dedicated, 240 s | normal | standard |
| civil-slow | slow | non-combat rules (no fire-rate penalty, 50% sustained, all weapons for 2.5 s) | normal | standard (armed traders, freighters, scavengers are common) |
| civil-nimble | nimble | non-combat rules | normal | standard |

Agility bands: dominance must hold at both ends of a band (the range factor is monotonic, so the ends are enough). A
hull within about ±15% of 110 uses the intersection of both bands' relations (an outfit is dropped only if dropped
in both).

## 7. Pre-run vs on demand

**Pre-run at import** (after each game update), in this order: layer 0, power (5), storage, fuel, engines,
regeneration, anti-missile (5 each), standard weapons (30).

**On demand, the first time a request needs it, then cached:**
- weapon goals: disable (plunderers, boarding flagships; slow and nimble), destroy, capture-intact, non-lethal;
- fighters and drones (fighter rules, tiny slots);
- capture targets; fights per restock other than 2;
- new fight lengths (burst, siege, chains);
- utility and effect lenses, built from the data: a lens gets a pass only if at least two in-play outfits carry its
  stat. Today that means heat, ion, scrambling, slowing, burn, disruption, corrosion, fuel damage, push, pull,
  piercing, blast, mining; and not discharge, leak, relative damage, cloak or heat protection (no outfits);
- enemy profiles (reweighted damage and protection lenses);
- credit caps (cost becomes a tier 1 stat for that pass).

**Never pruned:**
- outfits a request names (must have, allow by name, story minimums);
- outfits already installed, in refit and upgrade modes;
- tier 3 outfits, except by exact strict dominance;
- anything with an unknown attribute.

Cache key: game data hash + pruner version + pass id. A new game update invalidates everything; a new pruner
version invalidates only what it changes.

## 8. How the optimizer uses it

1. **Shape key.** Map the request onto closed conditions: solar case, combat case (agility band from the hull's stock
   agility, engagement, goal), pilot, mode. Open-ended fields (weights, minimums, budgets, tag lists) never select a
   pass; they narrow at run time.
2. **Select passes:** layer 0, plus one pass per family for the shape key. Missing specialty passes are computed and
   cached.
3. **Apply relations against this user's availability:** drop A only if every outfit in its "beaten by" entry is
   available to this user (and within copy limits). Otherwise A stays.
4. **Apply the never-pruned rules** (section 7).
5. **Keep the weapon reference set independent:** the average weapon suitability comes from availability, not from
   the pruned pool.

## 9. Safety net

- **Reporting:** "pruned N of M outfits (power X, engines Y, ...)", a flag to list every drop with what beats it, and
  `--no-prune`.
- **Polish retry:** the optimizer's polish stage re-tries the best few dropped outfits and reports any that would
  have improved the design. Any such report is a pruner bug.
- **Audit mode:** occasionally run with pruning off and compare scores.
- **Front size warnings:** a family front of one outfit for a pass is flagged.
- **Unknown attributes:** listed per game update for classification.

## 10. Performance

- Cheap passes first: strict dominance and ladders shrink the lists before any search is built.
- The power plant search re-solves only loads whose best plant used a banned outfit.
- Passes are independent and run in parallel across cores.
- Dominance families (everything except power) are pairwise comparisons over a few hundred outfits per pass; they
  should take seconds.

## 11. Changes from what is built today

| Today | Planned |
|---|---|
| Kept lists per pass | Relations per pass |
| Availability tiers sold / taken / all as passes, plus robust lists | One pass per condition; each relation records its replacement's tier, and availability is applied at load |
| Solar: none, dim, median (legacy), bright, max | dark, evader, normal, bright, max, aligned to the optimizer's constants |
| Steady-state energy and heat | Tier 1 stats at the optimizer's duty cycles |
| Generator storage flagged as an "other stat" | Storage is a tier 2 dimension (protects, never credits) |
| Strict dominance on power families only, ignoring weapon sub-blocks | Strict dominance on every family, with effective weapon values |

## 12. Open questions

1. ~~Whether to pre-run the two `disable` weapon cases~~ Decided: 6 cases; disable is on demand.
2. The reviewed tier table: every in-play attribute in tier 1, 2 or 3, per family (to draft with the optimizer
   session).
3. Load grids and reference loads per family: the power grid exists; engines and weapons need theirs.
4. Whether energy storage needs the solar axis (it barely draws power; 1 pass assumed).
5. Agility band edges: one split at 110, or more bands (the comfortable range keeps changing below 110).
