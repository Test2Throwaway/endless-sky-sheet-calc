# Design scenario brainstorm (notes, draft 1)

Working notes for choosing obsolescence passes. Tiers: **LC** likely/common, **LU** likely/uncommon,
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
