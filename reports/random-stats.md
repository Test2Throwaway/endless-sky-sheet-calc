# Random velocity and random lifetime, abstracted to the median

How the game applies them (`Projectile.cpp`):

- velocity = `velocity + Random::Real() × random velocity`: uniform between the two, so the **median is
  velocity + ½ × random velocity**. The game's AI aims with the same figure (`AI.cpp`). Random velocity can be
  negative (the UREB's electron bunches); the rule still holds.
- lifetime = `lifetime + Random::Int(random lifetime + 1)`: a whole number of frames from 0 to the random value,
  uniform, so the **median is lifetime + ½ × random lifetime**.
- A submunition's velocity is added to its parent's, so its median speed is the parent's speed plus this median.

Range uses the medians: median velocity × median lifetime (summed down the submunition chain), unless the weapon has
a range override. Values are per frame, as in the game data.

| # | Weapon | Projectile (if a submunition) | Velocity | Random velocity | **Median velocity** | Lifetime | Random lifetime | **Median lifetime** |
|---|---|---|---|---|---|---|---|---|
| 1 | "Ojet" Bimodal Coilgun | Bimodal Switch | 30 | 0 | **30** | 6 | 3 | **7.5** |
| 2 | Bimodal Coilgun Turret | Bimodal Switch | 30 | 0 | **30** | 6 | 3 | **7.5** |
| 3 | Bombardment Cannon | — | 6 | 1 | **6.5** | 150 | 0 | **150** |
| 4 | Bombardment Turret | — | 6 | 1 | **6.5** | 150 | 0 | **150** |
| 5 | Cluster Mine Layer | Korath Mine Submunition | 2 | 5 | **4.5** | 1000 | 60 | **1030** |
| 6 | Drag Cannon | Drag Projectile | 25 | 0 | **25** | 10 | 5 | **12.5** |
| 7 | External Launch Tube | Orchid Boost Stage Expended | -18 | 3 | **-16.5** | 300 | 0 | **300** |
| 8 | External Launch Tube | Orchid Divert Stage Expended | -12 | 3 | **-10.5** | 300 | 0 | **300** |
| 9 | Flamethrower | Flamethrower Projectile | 0 | 0 | **0** | 18 | 8 | **22** |
| 10 | Gatling Gun | gbullet | 0 | 8 | **4** | 20 | 5 | **22.5** |
| 11 | Gatling Turret | gbullet | 0 | 8 | **4** | 20 | 5 | **22.5** |
| 12 | Heavy Ion Cyclotron | Heavy Ion Fragment | 0 | 8 | **4** | 25 | 8 | **29** |
| 13 | Inhibitor Cannon | — | 36 | 0.5 | **36.25** | 24 | 0 | **24** |
| 14 | Inhibitor Turret | — | 36 | 0.5 | **36.25** | 24 | 0 | **24** |
| 15 | Ion Hail Turret | ion hail | 0 | 3 | **1.5** | 40 | 4 | **42** |
| 16 | Ion Rain Gun | — | 16 | 2 | **17** | 25 | 5 | **27.5** |
| 17 | Langrage Hyper-Heaver | Heaver Shard | 10 | 1.5 | **10.75** | 20 | 7.5 | **23.75** |
| 18 | Langrage Hyper-Heaver | Heaver Splinter | 0 | 0 | **0** | 20 | 7.5 | **23.75** |
| 19 | Locust Blaster | — | 10 | 2 | **11** | 40 | 0 | **40** |
| 20 | Locust Turret | — | 10 | 2 | **11** | 40 | 0 | **40** |
| 21 | Medium VLS | Nettle Flecks | 0 | 6 | **3** | 60 | 30 | **75** |
| 22 | Plasma Discharger | — | 10 | 0 | **10** | 64 | 12 | **70** |
| 23 | Plasma Discharger | plasma particle | 0 | 2 | **1** | 60 | 0 | **60** |
| 24 | Shard Fabricator | — | 15 | 0 | **15** | 40 | 20 | **50** |
| 25 | Shard Fabricator | Shard inactive | 0 | 0 | **0** | 60 | 40 | **80** |
| 26 | Small VLS | Nettle Flecks | 0 | 6 | **3** | 60 | 30 | **75** |
| 27 | Speckle Coilgun | Speck | 30 | 0.6 | **30.3** | 24 | 3 | **25.5** |
| 28 | Speckle Turret | Speck | 30 | 0.6 | **30.3** | 24 | 3 | **25.5** |
| 29 | Tiny VLS | Nettle Flecks | 0 | 6 | **3** | 60 | 30 | **75** |
| 30 | UREB Turret | GeV Electron Bunch | 300 | -210 | **195** | 12 | 3 | **13.5** |
