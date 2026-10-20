# Attribute tier table (draft for review)

How the pruner treats every attribute that in-play outfits use: 153 top-level attributes and 68 weapon keys,
counted from `data/outfits-in-play.md` and the game data. The **Optimizer** column is how the optimizer's
`calculator.py`, `solver.py` and `roles.py` treat each one today (checked by the optimizer session): **U** always
counted, **C** only when a role, flag or hull asks for it, **I** ignored. Any attribute becomes C when a role names it,
because roles can weight or require any attribute summed over the ship.

Design: `docs/pruner-design.md`. Directions and zero-value rulings: `docs/scenario-brainstorm.md`.

## Treatment codes

| Code | Tier | Meaning in a standard pass |
|---|---|---|
| **T** | 1 | **Traded:** converted into outfit space at the pass's rates (and duty cycle), so a rival can win by being cheaper overall. |
| **D** | 1 or 2 | **Dimension:** a rival must be no worse on it. Never converted, never a credit. Universal stats that can't be converted (mass) and conditional stats (storage, fuel, protections) are both D; the difference is only whether the optimizer counts it for every design. |
| **K** | 3 | **Keep:** an outfit with this is never pruned, unless the rival has exactly the same value. |
| **C** | – | **Capacity used:** a dimension where less is better; capacities never convert into each other. |
| **X** | – | **Class key:** outfits are only compared within the same value. |
| **–** | – | Cosmetic or metadata: ignored. |

Rules that apply on top of the table:

1. **Own family vs other families.** T applies only to an outfit's own family (section 3 lists who owns what). An
   attribute from another family's job is always D on that outfit: a thruster's cooling is traded in the engine
   family; a generator's storage is D in the power family.
2. **Known direction → D; unknown direction or an incomparable mechanic → K.** An attribute the optimizer ignores
   (I) but whose direction is clear (inaccuracy, heat damage) is a D: keeping the outfit with more of it is always
   safe, and the optimizer can value it later.
3. **Layer 0 (strict dominance) uses the direction column for everything**, including cost and every D and C, and
   still blocks on K.
4. **Unknown attributes are K** and are reported per game update.

## 1. Top-level attributes

### 1.1 Cosmetic and metadata (ignored)

`thumbnail`, `description`, `series`, `index`, `plural`, `display name`, `flare sprite`, `flare sound`,
`steering flare sprite`, `steering flare sound`, `reverse flare sprite`, `reverse flare sound`, `afterburner effect`,
`flotsam sprite`, `flotsam chance`, `jump effect`, `can jettison`, `unplunderable` (affects what can be looted from
the ship, not the design), `licenses` (availability only, applied at load).

### 1.2 Capacities used and special slots (C)

The optimizer treats all of these as hard fits (U, no value). Fit before dominance: a rival must use no more of
every capacity, and special slots are never interchangeable.

| Attribute | In-play outfits | Notes |
|---|---|---|
| outfit space | 539 | The base currency of every compensated cost. Negative = used. |
| weapon capacity | 172 | Guns, turrets, secondaries (and some reversers). |
| engine capacity | 145 | Engines (and a few turrets). |
| gun ports, turret mounts | 88, 71 | Slot type is also a class key (guns vs turrets). |
| cargo space | 4 | Negative = used (expansions, some tanks); positive = provided (D, see 1.8). |
| required crew | 46 | C against bunks. Also K when capture matters (see 1.9). |
| `<x> capacity` (javelin, torpedo, meteor, sidewinder, typhoon, rocket, gatling round, speck, nettle, finisher, thunderhead, swarm, railgun slug, tracker, star tail, spike, piercer, minelayer, firelight missile, orchid, firestorm torpedo, emp torpedo) | 2–6 each | Ammo storage. Launchers provide it, ammo uses it: a pair, judged together (X on ammo type). |
| reactor upgrades, relay upgrades, nanite upgrades, solar cell, shield connection point, magnetic nozzle | 2–5 each | Upgrade slots: the base outfit and its add-ons are judged as combinations. |
| anchor point, spinal mount, multimodal armor, asteroid mount small, asteroid mount jd, lasing power | 1–4 each | Special slots, hull- or outfit-provided. Never interchangeable. |

### 1.3 Power and cooling (owned by the power family)

| Attribute | Outfits | Optimizer | Direction | Power family | Other families |
|---|---|---|---|---|---|
| energy generation | 65 | U | higher | T (the plant search) | T (credited at the pass rate) |
| energy consumption | 29 | U | lower | T | T |
| heat generation | 83 | U | lower | T | T |
| cooling | 19 | U | higher | T (ladder) | T (credited, e.g. radiant thrusters) |
| active cooling, cooling energy | 8, 8 | U | higher, lower | T (plant search) | D (works only when hot; never credited outside power) |
| solar collection | 8 | U | higher | T at the pass's solar case | T |
| solar heat | 11 | U | lower | T at the pass's solar case | T |
| heat dissipation | 2 | U | higher | D | D |
| heat capacity | 3 | U | higher | D | D |
| cooling inefficiency | 1 | U | lower | K (non-linear in the number of cooling outfits) | K |
| energy capacity | 61 | U | higher | D (storage family's job) | D |
| overheat damage rate | 2 | I | lower | K (changes overheating behaviour) | K |

### 1.4 Movement (owned by the engine family)

| Attribute | Outfits | Optimizer | Direction | Engines | Other families |
|---|---|---|---|---|---|
| thrust, turn | 74, 72 | U | higher | D (the values being bought) | D |
| thrusting energy, thrusting heat | 70, 75 | U at 70% duty | lower | T at 70% | T at 70% |
| turning energy, turning heat | 68, 72 | U at 30% duty | lower | T at 30% | T at 30% |
| negative thrusting energy (energy made while thrusting) | few | U on nimble ships only | higher | K (agility-dependent) | K |
| reverse thrust | 26 | C | higher | D | D |
| reverse thrusting energy, heat | 26, 26 | C | lower | D (reverse is conditional, so its costs aren't traded) | D |
| afterburner thrust, energy, heat, fuel, shields | 4–15 | C | higher; lower | X (afterburner is a presence tag), then D | X |
| thrusting fuel | 2 | U (fight fuel) | lower | D | D |
| drag reduction, inertia reduction | 4, 2 | U | higher | D | D |
| drag (an outfit adding drag) | 3 | U | lower | D | D |
| slowing resistance | 8 | C | higher | D | D |
| mass | 581 | U | lower | D (strict option: a lighter rival also needs at least as much heat capacity) | D |

### 1.5 Regeneration (owned by the regeneration family)

| Attribute | Outfits | Optimizer | Direction | Regeneration | Other families |
|---|---|---|---|---|---|
| shield generation, hull repair rate | 33, 13 | U | higher | D (the values being bought) | D |
| shield energy, shield heat, hull energy, hull heat | 30, 9, 14, 8 | U (recovery and combat) | lower | T at the recovery duty | T |
| shield fuel | 2 | U | lower | D | D |
| delayed shield generation, energy, heat | 3, 2, 2 | U | higher; lower | X (a different regen mechanic), then D | X |
| shield protection, hull protection | 5, 2 | U (effective shields and hull) | higher | D | D |
| shield / hull generation, energy, heat and repair multipliers | 1–4 | U | higher (generation, repair); lower (energy, heat) | K (value depends on the other outfits; applied as 1 + value) | K |
| shield delay, depleted shield delay | 2, 1 | I (a known gap) | lower | K (not in the recovery model yet) | K |

### 1.6 Fuel and travel (owned by the fuel family)

| Attribute | Outfits | Optimizer | Direction | Fuel | Other families |
|---|---|---|---|---|---|
| fuel capacity | 11 | U | higher | D | D |
| fuel generation | 3 | U | higher | D | D |
| ramscoop | 9 | U by default (needs_ramscoop) | higher | D, and X (ramscoop tag) | X |
| jump fuel | 5 | U (defaults 100/150/200) | lower | D | D |
| hyperdrive, jump drive, scram drive, quantum keystone | 3, 2, 1, 3 | U by default (needs_drives); scram drive I | – | X (presence tags) | X |
| jump range, jump speed | 1, 4 | C | higher | D | D |
| fuel protection | 1 | C | higher | D | D |

### 1.7 Protection and resistance (any family)

`ion resistance`, `scramble resistance`, `ion protection`, `slowing resistance` and the other protections and
resistances: optimizer C (metrics only), direction higher, treatment **D** everywhere. Note the Ultracapacitors'
*negative* ion protection: a value below 0 is worse, so D handles it.

### 1.8 Utility and systems (owned by the systems family; strict dominance only)

| Attribute | Outfits | Optimizer | Direction | Treatment |
|---|---|---|---|---|
| cargo space (positive) | 4 | C (metric) | higher | D |
| bunks | 3 | U fit, C value | higher | D |
| tactical, cargo, outfit, asteroid scan power; cargo, outfit scan efficiency; atmosphere scan | 4–9 | C | higher | D |
| radar jamming, optical jamming, scan interference | 4–5 | C | higher | D |
| cargo scan opacity, outfit scan opacity | 2, 1 | C | higher | D |
| holographic entertainment | 1 | C | higher | D |
| illegal | 2 | C (tag) | – | X (presence tag) |
| automaton | 1 | U fit | – | X |
| scan brightness, operating costs | 1, 1 | I | lower | D |
| map, map minables | 1 | I | – | K (Local Map is a one-off) |
| minable, installable < 0 | 16 | excluded | – | not designable; ignored |

### 1.9 Boarding and capture

| Attribute | Outfits | Optimizer | Direction | Treatment |
|---|---|---|---|---|
| capture attack, capture defense | 17, 22 | I (Hand to Hand excluded today; a known gap) | higher | K: value is capped by crew, so neither counts nor single comparisons are safe |
| required crew (on capture ships) | – | – | – | K whenever either outfit has capture stats |

### 1.10 Identity and availability

| Attribute | Optimizer | Treatment |
|---|---|---|
| unique | U (copy limit 1; only for hero ships) | X (copy limit) |
| linked | I | X (pairs: an outfit and what it links to are judged together) |
| cost | I (printed, not scored) | D in layer 0 (so it stays valid under credit caps); ignored in standard passes; T in credit-cap passes |

## 2. Weapon keys (weapons and anti-missile families)

Derived values are compared, not raw fields: shots per second (60 ÷ reload; burst count and burst reload don't
change the average), range (range override, else velocity × total lifetime with submunitions), projectile speed,
damage per second by type (including submunitions unless excluded).

| Key | Weapons | Optimizer | Direction | Treatment (standard weapon passes) |
|---|---|---|---|---|
| shield damage, hull damage (per second) | 117 | U (weighted by goal) | higher | D (the values being bought) |
| reload | 157 | U (fire rate) | lower | D via shots per second |
| burst count, burst reload | 37 | not needed | – | ignored (average rate is 1 ÷ reload) |
| firing energy, firing heat (per second) | 155 | U (combat duty) | lower | T at the case's combat duty |
| firing fuel | 5 | U | lower | D |
| firing force (recoil) | 24 | I | unclear | K |
| firing ion, firing hull, relative firing shields | 1 each | I | lower | D |
| lifetime, random lifetime, velocity, random velocity, velocity override, range override | 3–153 | U (range, speed) | higher | D via derived range and speed, using the medians: velocity + ½ random velocity, lifetime + ½ random lifetime (`reports/random-stats.md`) |
| acceleration, drag (projectile) | 28, 32 | U (speed) | higher, lower | D via derived speed |
| inaccuracy | 134 | I | lower | D |
| turret turn | 56 | U (turrets) | higher | D (absent on a turret = 240°/s) |
| homing, tracking (radar, optical, infrared), turn (projectile) | 4–31 | U (homing exempts turret turn) | – | X (homing), then D on tracking |
| ammo | 39 | U | – | X (which ammo); ammo-free counts as unlimited |
| missile strength | 37 | C (missile tag) | – | X (missile or not), then D |
| anti-missile | 13 | U | higher | D (anti-missile family) |
| tractor beam | 2 | C | higher | X (tag), then D |
| hit force | 60 | C (push/pull metrics) | – | X by sign (push vs pull), then K outside the push/pull lens |
| heat, ion, scrambling, slowing, burn, disruption, corrosion, fuel, energy damage | 1–18 | I (disruption C via tag) | higher | X (effect vector), then D |
| piercing | 10 | C (capture-intact check) | goal-dependent | K (good for destroy, bad for disable and capture) |
| minable damage, prospecting | 7, 5 | I | higher | X (mining), then D |
| penetration count | 2 | I | higher | D (0 = unlimited) |
| blast radius, trigger radius, split range | 15, 9, 1 | I | unclear | K, except D on blast radius when the weapon is safe |
| safe | 4 | I | – | X |
| cluster, stream, phasing, no damage scaling | 1–17 | I | – | X |
| damage dropoff, dropoff modifier | 2 | I (a known gap) | – | X (dropoff or not); dropoff modifier defaults to 1 |
| triggers nuke alert | 1 | I | – | X |
| submunition | 31 | U (damage, range, speed) | – | judged through the derived values |
| sprite, sound, icon, effects, hardpoint sprite and offset, fade out | many | – | – | ignored |

## 2a. Weapon lenses (built: `sheetcalc/weapons.py`)

Two lens passes run after strict dominance. A lens compares only the stats one kind of request cares about, so
its drops apply only to that kind of request. Weapons are compared within their category (guns, turrets,
secondaries); outfit attributes, availability tiers and copy limits use the strict rules.

**Damage lens** (regular fighting weapons for general-purpose combat roles, such as the Kar Ik Vot 349). Weapons
with shield or hull damage that aren't anti-missile or tractor beams. Compared:

1. shield damage and hull damage per second (higher). With submunitions: the shot always splits and 80% of the
   final submunitions hit, for every such weapon.
2. firing energy, heat, force, fuel, ion, hull and relative firing shields per second (lower)
3. velocity (higher): the median, or velocity override where set
4. range (higher): range override where set, else velocity × median total lifetime including submunitions
5. inaccuracy (lower), projectile turn (higher), homing (having it is better), missile strength (higher)
6. turret turn on turrets (higher; absent means 240°/s)
7. ammo: needing ammunition, or a different one, never wins; with the same ammunition, less per second is better

Ignored: effect damages, hit force, piercing, no damage scaling, projectile drag and acceleration (already in
range), tracking, blast and trigger radius, split range, penetration count, damage dropoff, cluster, stream,
safe, phasing, nuke alert, burst timing, cosmetics.

**Anti-missile lens** (anti-missile turrets, compared only with each other; every combat ship wants some):
anti-missile strength, shots per second, range (higher); firing energy and heat per second (lower); ammo as
above. Turret turn is ignored: anti-missile aims instantly (`Hardpoint::FireSpecialSystem`). No damage weapon has
anti-missile and no anti-missile turret deals damage, so the two lenses never overlap.

## 3. Family ownership (where T applies)

| Family | Owns (its T stats) |
|---|---|
| Power | energy generation, consumption, heat generation, cooling, active cooling, solar |
| Engines | thrusting energy and heat (70%), turning energy and heat (30%) |
| Regeneration | shield and hull energy and heat (recovery duty) |
| Weapons, anti-missile | firing energy and heat (combat duty of the case) |
| Fuel, storage, systems | none: everything there is D, C, X or K |

Every family also trades the power stats on its outfits (energy generation and consumption, heat, cooling, solar)
at the pass's rates, because every ship pays for power and cooling.

## 4. Open points for review

1. **Mass:** the strict option (a lighter rival also needs at least as much heat capacity) or plain lower-is-better.
2. **Reverse thrust:** C in the optimizer, so its energy and heat are D, not traded. Trading them would prune more
   reversers, but would assume every ship reverses.
3. **Energy capacity:** U in the optimizer (energy-per-shot rule and combat drain), but D here, so storage is never
   credited. That's deliberately timid.
4. **Inaccuracy and the effect damages:** D, so they protect outfits even though the optimizer ignores them today.
   The alternative is to ignore them until the optimizer scores them, which would prune more weapons.
5. **Hit force:** K outside the push/pull lens. 60 weapons have some hit force, so this blocks a lot of weapon
   pruning. An alternative is D on push force (more is better for most combat) with pull kept separate.
