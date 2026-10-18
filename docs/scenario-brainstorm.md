# Design scenario brainstorm (notes, draft 2)

Working notes for choosing obsolescence passes. Draft 2 merges the optimizer session's independent list (135
scenarios, `aside/design-scenarios.md` in the optimizer repo, commit 20f0953): together about 165 distinct scenarios. Tiers: **LC** likely/common, **LU** likely/uncommon,
**UU** unlikely/uncommon. "Drives" says what changes which outfits matter. Sources: the legacy workbook's tabs
(Damage Weapons, Utility Weapons: shield disabling / moving / slowing / shield disruption / tractor beam / heat damage
/ ion, Anti-Missile, Jammers, Scanners, Fuel, Cargo & Outfit Expansions, Batteries, Cooling, Shields, Drives), the
game's weapon and ship attributes (`Weapon.cpp`, `Ship.cpp`), the optimizer's roles and metrics, and player
discussions (Steam forums: boarding flagships, pirate-hunting loops).

## Combat: general shapes

| # | Scenario | Tier | Drives |
|---|---|---|---|
| 1 | Dedicated warship (line ship) | LC | sustained dps, 4 min sustain, survivability route |
| 2 | Escort | LC | 90 s sustain, keep up with fleet speed |
| 3 | Player flagship brawler (hero) | LC | uniques allowed, no afterburner, all-round |
| 4 | Interceptor: catch and kill small ships | LC | speed, acceleration, fire rate, projectile speed |
| 5 | Dogfighter: evasive, out-turns | LC | turn, agility, guns on a nimble hull |
| 6 | Tank / brick: slow, outlasts | LC | shield regen, hull repair, protection, pull force |
| 7 | Glass cannon / alpha striker: wins in seconds | LU | burst dps, batteries, short fight |
| 8 | Long-range artillery / sniper | LU | range, turrets, projectile speed |
| 9 | Close-range brawler | LU | raw dps, short range is fine, durability |
| 10 | Missile boat | LU | secondary weapons, ammo depth, fights per restock, homing |
| 11 | Torpedo bomber vs capitals | LU | big single hits, piercing, hull damage |
| 12 | Turret platform (slow hull, all turrets) | LC | turret turn, range, gun-on-slow-ship penalty avoided |
| 13 | Gunboat (forward guns only) | LC | agility needed to aim guns |
| 14 | Point-defence picket for a fleet | LU | anti-missile, optical jamming |
| 15 | Anti-fighter / anti-drone screen | LU | fire rate, tracking, blast radius |
| 16 | Capital killer (4 min vs big hulls) | LU | hull dps, piercing, relative hull damage |
| 17 | Pirate / bounty hunter | LC | kill fast, chase, decent regen |
| 18 | Raider: hit and run | LU | speed, afterburner, burst |
| 19 | Blockade runner | LU | survive and escape: speed, jammers, regen |
| 20 | Kiter: outranges and outruns | LU | range > enemy, speed, reverse thrust |
| 21 | Fleet anchor / carrier mothership | LU | fighter and drone bays, regen, range |
| 22 | Fighter (carried) | LU | fighter weapon rules, tiny hull, lumpy ladders |
| 23 | Drone (carried, uncrewed) | UU | no crew, fighter rules |
| 24 | Mine layer / area denial | UU | mines, blast radius, ammo |
| 25 | Nuke boat | UU | nuke-alert weapons, blast radius |
| 26 | Swarm-buster vs clustered enemies | UU | blast radius, submunitions |

## Combat: disable, capture, plunder

| # | Scenario | Tier | Drives |
|---|---|---|---|
| 27 | Disabler (stop ships, don't destroy) | LC | shield damage ≫ hull damage (workbook: shield disabling) |
| 28 | Boarding flagship (capture whole ships) | LC | crew, bunks, capture attack, hand-to-hand outfits |
| 29 | Capture-intact specialist | UU | instantaneous weapons, keep target shields ≥ 50% |
| 30 | Plunderer / looter | LU | disable + cargo + tractor beam |
| 31 | Post-battle scavenger | LU | tractor beam, cargo, survive the battle |
| 32 | Shield stripper support | LU | shield damage per space (Ka'het Annihilator class) |
| 33 | Shield breaker support | UU | disruption damage (workbook: shield disruption) |
| 34 | Ion drainer: shut down enemy power | UU | ion and scrambling damage (workbook: ion) |
| 35 | Heat killer: overheat the enemy | UU | heat damage, burn (workbook: heat damage) |
| 36 | Snare: slow enemies for the fleet | UU | slowing damage (workbook: slowing) |
| 37 | Grappler: pull enemies into range | UU | pull force (workbook: moving), tank route |
| 38 | Repulsor: push enemies away | UU | push force, kiting |
| 39 | Damage-over-time attacker | UU | corrosion, leak, burn, discharge damage |
| 40 | Fuel stranding attacker | UU | fuel damage |
| 41 | Energy drainer | UU | energy damage |
| 42 | Giant-killer by percentage | UU | relative shield / hull damage |

## Defence and survival shapes

| # | Scenario | Tier | Drives |
|---|---|---|---|
| 43 | Shield tank with protection | LU | shield regen, shield protection, cortexes, relays |
| 44 | Hull tank | UU | hull repair, nanites, hull protection |
| 45 | Fast-recovery skirmisher | UU | shield delay, depleted shield delay, repair delay |
| 46 | Missile-proof brick (vs missile-heavy enemies) | LU | anti-missile + radar/optical jamming |
| 47 | Ion-hardened (vs Korath/ion users) | UU | ion protection / resistance |
| 48 | Heat-hardened (vs heat weapons) | UU | heat capacity, heat protection |
| 49 | Exotic-resistant (corrosion, leak, burn, discharge...) | UU | matching protections and resistances |
| 50 | Overheat-tolerant berserker | UU | overheat damage threshold, runs hot |
| 51 | Disable-resistant (survives being disabled) | UU | disabled recovery time, hull threshold |

## Stealth, sensors, electronic warfare

| # | Scenario | Tier | Drives |
|---|---|---|---|
| 52 | Smuggler | LU | scan interference, cargo/outfit scan opacity, cargo |
| 53 | Cloaked ambusher | UU | cloak, cloaked firing, cloaking energy/heat/fuel |
| 54 | Cloaked scout / courier | UU | cloak, speed, jumps, no weapons |
| 55 | Electronic warfare escort | UU | radar/optical jamming for the fleet |
| 56 | Scanner / survey ship (missions that need scans) | LU | outfit / cargo / tactical scan power and efficiency |
| 57 | Bounty tracker | UU | tactical scanner, speed |

## Trade, transport, travel

| # | Scenario | Tier | Drives |
|---|---|---|---|
| 58 | Bulk freighter | LC | cargo space, cargo expansions |
| 59 | Armed merchant | LC | cargo + enough weapons and regen to deter |
| 60 | Fast courier (rush missions) | LC | speed, jumps, small cargo |
| 61 | Passenger liner | LC | bunks, comfort outfits |
| 62 | Mixed cargo and passengers | LU | cargo + bunks |
| 63 | Peaceful-area freighter | LU | cargo, jumps, no jump drive / anti-missile |
| 64 | Fleet supply hauler | LU | cargo for the fleet's plunder, keeps up |
| 65 | Fuel tanker for a fleet | LU | fuel capacity, ramscoop, fuel generation |
| 66 | Long-range explorer (never refuels) | LU | ramscoop, fuel generation, fuel capacity |
| 67 | Dark-space explorer (no stars on route) | UU | fuel generation not ramscoop, no solar |
| 68 | Jump-drive scout | UU | jump drive only, jump range |
| 69 | Mission ferry (escort passengers through danger) | LU | bunks + survivability |

## Mining and industry

| # | Scenario | Tier | Drives |
|---|---|---|---|
| 70 | Miner | LU | asteroid scan power, minable damage, prospecting, cargo, tractor beam |
| 71 | Defended miner | UU | miner + survivability |
| 72 | Prospector scout | UU | asteroid scan power only |

## Economy, progression and availability

| # | Scenario | Tier | Drives |
|---|---|---|---|
| 73 | Starting-ship upgrade | LC | cheap, sold only, no military licences |
| 74 | Budget build (credit cap) | LC | outfit cost (not modelled today) |
| 75 | Cheapest ship that passes a role (fleet filler) | LU | cost-minimal |
| 76 | No-budget endgame | LC | best of everything in play |
| 77 | Licence-limited mid game | LC | sold pool shaped by licences |
| 78 | Faction-locked build (Hai only, Wanderer only, Remnant...) | LU | availability by faction |
| 79 | Plunder-only build | UU | only what you can take from ships |
| 80 | Re-buyable build (replaceable after losses) | LU | sold only |
| 81 | Mass-produced escort (many identical copies) | LU | sold only, copy limits irrelevant, cost |
| 82 | Hero flagship with story uniques | LU | unique outfits |
| 83 | Story mission constraints (carry N passengers / tons) | LU | hard minimums |
| 84 | Refit an existing ship (keep installed outfits) | LC | installed outfits must never be pruned |
| 85 | Partial refit (change only weapons, or only engines) | LU | one family varies, others fixed |

## Mobility specifics

| # | Scenario | Tier | Drives |
|---|---|---|---|
| 86 | Top-speed racer | UU | drag reduction, thrust/mass |
| 87 | Agility king | UU | turn, inertia reduction |
| 88 | Reverse-thrust kiter (nimble) | UU | reverse thrust |
| 89 | Afterburner sprinter | LU | afterburner thrust, fuel |
| 90 | Heavy hauler that still turns | LC | minimum turn rate |
| 91 | Fleet-speed matcher (exactly keep up) | LU | speed target band |

## Environment

| # | Scenario | Tier | Drives |
|---|---|---|---|
| 92 | Bright-star operations | UU | solar, solar heat |
| 93 | Must run dark | UU | no solar at all |
| 94 | Dim-star evader | UU | low solar, long endurance |
| 95 | Low solar-wind regions | UU | ramscoop weak: fuel capacity, generation |
| 96 | Long fights (sieges beyond 4 min) | UU | true sustain, no batteries |
| 97 | Short skirmishes (under 30 s) | LU | batteries, burst |
| 98 | Many fights between restocks | UU | ammo depth, energy weapons |
| 99 | Energy weapons only (never restocks ammo) | LU | no ammo-using weapons |
| 100 | Ammo-heavy, energy-light | UU | launchers, small power plant |

## Hull shapes

| # | Scenario | Tier | Drives |
|---|---|---|---|
| 101 | Tiny hull | LC | lumpy whole-outfit ladders, small outfits |
| 102 | Medium hull | LC | middle of the ladders |
| 103 | Capital hull | LC | asymptotic prices, big outfits |
| 104 | Gun-heavy hull | LC | gun ports ≫ turret mounts |
| 105 | Turret-heavy hull | LC | turret mounts ≫ gun ports |
| 106 | Hull with special slots (anchor points, spinal mounts, bays) | UU | slot-specific outfits |
| 107 | Engine-capacity-starved hull | LC | thrust per engine capacity |
| 108 | Weapon-capacity-starved hull | LC | dps per weapon capacity |
| 109 | Very heavy hull | LU | mass makes agility and heat capacity dominate |
| 110 | Shortlist of hulls compared | LC | prune per hull band, not per hull |
| 111 | Fleet of complementary hulls | UU | beyond single-ship design |

## Added from the optimizer session's list (not in draft 1)

Flotsam farmer of a specific drop (e.g. Antimatter Power Cell) · gas-giant lander (gaslining) · research vessel
(Research Laboratory) · decoy tank (Decoy Plating) · self-destruct decoy · Holovid / Phantom Pallet trickster ·
anti-cloak hunter · scrambler (make targets miss) · beam boat (instantaneous only) · missile-only ship · mixed
primaries + secondaries (80% secondary window) · gravity anchor (push + pull) · disruptor + hull combo · spinal-mount
warship · cloaked transport · escort-carrier hybrid · carrier + its fighters designed together · fleet line ship
flown by AI · hero all-rounder (warship + freighter + escort) · stock-loadout upgrade · upgrade path (next affordable
step) · speedrun (best design before a story point) · arena duel vs a named hull · counter-build vs a named
government · siege vs station defences · faction-tech builds (Wanderer, Hai, Pug, Coalition/Heliarch, Korath
territory, Remnant space) · human-tech purist / one-race showcase · source- and government-limited availability ·
Quarg hunting · max cargo with no weapons · max jump range · max bunks · immobile regen fortress · minimum mass /
heat / energy ships · zero-crew automaton · superheavy hulls · unique-only stress test · fleet repair tender (note:
the game has no ally repair beyond fuel transfer, so this one probably isn't real).

## Axes (from both lists)

A scenario = an archetype (~45-60) with a setting on each axis:

| Axis | Values | Closed? |
|---|---|---|
| Engagement | none, burst ~30 s, escort 90 s, dedicated 240 s, siege ~600 s | closed |
| Light | dark, dim, median, bright, star-hugging | closed |
| Enemy profile | generic, shield-heavy, hull-heavy, missile swarm, fighter swarm, heat, ion/energy drain, slowing, push/pull, disruption, cloaked | closed (~11) |
| Pilot | hero, AI escort, carried fighter, drone | closed |
| Availability | per user (licences x governments x sources); tiers sold / taken / all | open; tiers closed |
| Money | unlimited, credit cap | open |
| Hull band | agility band, mass band, slot shape (guns vs turrets, spinal, bays, anchors) | bands closed |
| Mode | new design, refit (installed fixed), partial refit, upgrade step | closed |

## Reality check: which lenses have outfits in play

Counted in the current in-play list (`data/outfits-in-play.md`):

| Stat | In-play outfits | | Stat | In-play outfits |
|---|---|---|---|---|
| heat damage | 18 | | capture attack | 17 |
| ion / scrambling damage | 10 / 10 | | capture defense | 22 |
| slowing damage | 6 | | anti-missile | 13 |
| burn damage | 4 | | tactical / cargo / outfit scan | 9 / 7 / 5 |
| disruption damage | 3 | | asteroid scan / minable damage | 8 / 7 |
| corrosion / fuel damage | 2 / 2 | | radar / optical jamming | 5 / 4 |
| energy damage | 1 | | scan interference | 5 |
| discharge, leak, relative damage | **0** | | shield protection | 5 |
| hit force (push/pull) | 60 | | ion protection | 2 |
| piercing | 10 | | heat protection, cloak | **0** |
| blast radius | 15 | | tractor beam | 2 |

So lenses should be built from the data: a lens gets a pass only if at least two in-play outfits carry its stat (a
lone outfit is kept anyway), and empty lenses (discharge, leak, relative damage, cloak, heat protection for this
player) cost nothing.

## Ramifications

### For the pruner (sheet calc)

1. **At import: strict dominance over every attribute.** The user's top priority. A is dropped only if some B is at
   least as good on *every* attribute A has (direction-aware: more thrust is better, more mass, cost, heat, energy
   draw is worse), strictly better on one, no more restricted in copies or availability tier, and the same kind of
   outfit (same slot type, ammo, linked outfits). Unknown-direction attributes block. Because it ignores lenses, it
   is valid for every scenario above, including credit caps (cost is an attribute). This needs a table of every
   attribute's direction; unknown ones are listed so they can be classified.
2. **Everything beyond that is relations, not lists.** Axes multiply to tens of thousands of shapes, so the smart
   passes store "A is beaten by B (or this set), valid over this region of the axes, replacement from tier T". A
   request becomes a set filter.
3. **Wider value vectors.** Each workbook effect sheet is a value axis (heat, ion, scrambling, slowing, disruption,
   burn, corrosion, fuel, energy damage, push/pull, piercing, blast, anti-missile, tractor, minable damage), plus
   protections, jamming, scanning, capture, bunks, cargo. Dominance must hold on every axis any lens in the region
   values.
4. **Enemy profiles are lenses** that reweight damage axes. Splitting weapons by effect, as the workbook does, maps
   directly.
5. **Power stays as it is, re-aligned** to the optimizer's light bands and engagement lengths (burst and siege make
   batteries a real family).
6. **Hull facts as bands** (agility, mass, slot shape). Exact capacities stay with the optimizer's own filter.
7. **Pairs and limits:** launchers + ammo + racks, reactors + overclockers, solar battery + cells; copy-limited
   outfits; small x2 vs large x1.
8. **Refit modes:** outfits already installed are never pruned.
9. **Hand to Hand outfits are in scope** (capture attack/defense) for boarding scenarios.
10. **Report the front size** per family and region; a front of 1 is a warning.

### For the optimizer

1. Map a request onto the closed axes (a shape key); open-ended fields narrow at run time and never prune.
2. Apply relations: drop A only if its replacement is available to this user.
3. New features most scenarios need: credit cap and cost scoring, enemy profiles, effect-damage scoring, Hand to Hand
   outfits in the pool, bunks/mining/smuggling/scanning metrics, light as a request field, burst and siege lengths,
   pilot axis, carriers and fleets, refit and upgrade modes.
4. Safety net: polish re-tries the best dropped outfits; CLI reports what was pruned; `--no-prune`.
5. Keep the weapon reference set independent of pruning.
