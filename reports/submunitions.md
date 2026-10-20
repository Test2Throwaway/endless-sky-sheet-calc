# Submunition damage: 80% of final submunitions hit

How the game works (Weapon::TotalDamage, Projectile.cpp): a projectile that hits a ship directly deals its own damage plus
the full total of all its submunitions. Submunitions spawn only when a projectile's lifetime runs out (no in-play weapon
uses `spawn on` or `exclude submunition damage`), and a projectile that splits deals no damage itself. Negative damage on
a parent only adjusts what a direct hit deals.

So, assuming every shot splits and 80% of its final submunitions (those with no submunitions of their own) hit:

**damage per shot = 0.8 × Σ (count × damage of each final submunition)**; per second = per shot × 60 ÷ reload.

*Direct hit* is what a shot deals if the parent hits before splitting (the number the game displays), for comparison.

## 1. "Ojet" Bimodal Coilgun (Guns)

Reload 30 frames: 2.00 shots/s.

| Damage type | Final submunitions (100%) | **80% per shot** | **80% per second** | Direct hit per shot |
|---|---|---|---|---|
| hull damage | 42 | **33.6** | **67.2** | 135 |
| shield damage | 144 | **115.2** | **230.4** | 50 |
| hit force | 0 | **0** | **0.0** | 120 |

Submunition chain (own stats; ✱ = final submunition):

- 3 × **Bimodal Switch** ✱ (3 per shot): shield damage 48, hull damage 14; lifetime 6, velocity 30

## 2. Asteroid Weapon Small (Guns)

Reload 60 frames: 1.00 shots/s.

| Damage type | Final submunitions (100%) | **80% per shot** | **80% per second** | Direct hit per shot |
|---|---|---|---|---|
| hull damage | 350 | **280** | **280.0** | 950 |
| hit force | -2100 | **-1680** | **-1680.0** | 1800 |
| slowing damage | 28 | **22.4** | **22.4** | 0 |

Submunition chain (own stats; ✱ = final submunition):

- 7 × **Asteroid Circle Submunition** ✱ (7 per shot): hull damage 50, slowing damage 4, hit force -300; lifetime 390

## 3. Drag Cannon (Guns)

Reload 45 frames: 1.33 shots/s.

| Damage type | Final submunitions (100%) | **80% per shot** | **80% per second** | Direct hit per shot |
|---|---|---|---|---|
| hull damage | 144 | **115.2** | **153.6** | 144 |
| shield damage | 156 | **124.8** | **166.4** | 156 |
| slowing damage | 1.35 | **1.08** | **1.4** | 1.35 |

Submunition chain (own stats; ✱ = final submunition):

- 3 × **Drag Projectile** ✱ (3 per shot): slowing damage 0.45, shield damage 52, hull damage 48; lifetime 10, velocity 25

## 4. Heavy Ion Cyclotron (Guns)

Reload 1 frames: 60.00 shots/s.

| Damage type | Final submunitions (100%) | **80% per shot** | **80% per second** | Direct hit per shot |
|---|---|---|---|---|
| hull damage | 4.41 | **3.528** | **211.7** | 4.41 |
| shield damage | 5.37 | **4.296** | **257.8** | 5.37 |
| hit force | 13.5 | **10.8** | **648.0** | 13.5 |

Submunition chain (own stats; ✱ = final submunition):

- 3 × **Heavy Ion Fragment** ✱ (3 per shot): hit force 4.5, shield damage 1.79, hull damage 1.47; lifetime 25

## 5. Plasma Discharger (Guns)

Reload 40 frames: 1.50 shots/s.

| Damage type | Final submunitions (100%) | **80% per shot** | **80% per second** | Direct hit per shot |
|---|---|---|---|---|
| hull damage | 39 | **31.2** | **46.8** | 78 |
| shield damage | 33 | **26.4** | **39.6** | 66 |
| minable damage | 90 | **72** | **108.0** | 180 |

Submunition chain (own stats; ✱ = final submunition):

- 5 × **plasma particle** ✱ (5 per shot): shield damage 6.6, hull damage 7.8, minable damage 18; lifetime 60

## 6. Proton Gun (Guns)

Reload 8 frames: 7.50 shots/s.

| Damage type | Final submunitions (100%) | **80% per shot** | **80% per second** | Direct hit per shot |
|---|---|---|---|---|
| hull damage | 25.2 | **20.16** | **151.2** | 25.2 |
| shield damage | 30.3 | **24.24** | **181.8** | 30.3 |
| hit force | 27 | **21.6** | **162.0** | 27 |

Submunition chain (own stats; ✱ = final submunition):

- 3 × **Proton Fragment** ✱ (3 per shot): hit force 9, shield damage 10.1, hull damage 8.4; lifetime 24

## 7. Speckle Coilgun (Guns)

Reload 18 frames: 3.33 shots/s.

| Damage type | Final submunitions (100%) | **80% per shot** | **80% per second** | Direct hit per shot |
|---|---|---|---|---|
| hull damage | 48 | **38.4** | **128.0** | 48 |
| shield damage | 24 | **19.2** | **64.0** | 24 |
| hit force | 18 | **14.4** | **48.0** | 18 |

Submunition chain (own stats; ✱ = final submunition):

- 1 × **Speck** ✱ (1 per shot): shield damage 24, hull damage 48, hit force 18; lifetime 24, velocity 30

## 8. Twin Blaster (Guns)

Reload 12 frames: 5.00 shots/s.

| Damage type | Final submunitions (100%) | **80% per shot** | **80% per second** | Direct hit per shot |
|---|---|---|---|---|
| hull damage | 13.2 | **10.56** | **52.8** | 13.2 |
| shield damage | 21.2 | **16.96** | **84.8** | 21.2 |

Submunition chain (own stats; ✱ = final submunition):

- 1 × **Blaster Submunition** ✱ (1 per shot): shield damage 10.6, hull damage 6.6; lifetime 48, velocity 10.625
- 1 × **Blaster Submunition** ✱ (1 per shot): shield damage 10.6, hull damage 6.6; lifetime 48, velocity 10.625

## 9. Twin Modified Blaster (Guns)

Reload 12 frames: 5.00 shots/s.

| Damage type | Final submunitions (100%) | **80% per shot** | **80% per second** | Direct hit per shot |
|---|---|---|---|---|
| hull damage | 17.6 | **14.08** | **70.4** | 17.6 |
| shield damage | 26.4 | **21.12** | **105.6** | 26.4 |

Submunition chain (own stats; ✱ = final submunition):

- 1 × **Modified Blaster Submunition** ✱ (1 per shot): shield damage 13.2, hull damage 8.8; lifetime 48, velocity 10
- 1 × **Modified Blaster Submunition** ✱ (1 per shot): shield damage 13.2, hull damage 8.8; lifetime 48, velocity 10

## 10. Bimodal Coilgun Turret (Turrets)

Reload 15 frames: 4.00 shots/s.

| Damage type | Final submunitions (100%) | **80% per shot** | **80% per second** | Direct hit per shot |
|---|---|---|---|---|
| hull damage | 42 | **33.6** | **134.4** | 135 |
| shield damage | 144 | **115.2** | **460.8** | 50 |
| hit force | 0 | **0** | **0.0** | 120 |

Submunition chain (own stats; ✱ = final submunition):

- 3 × **Bimodal Switch** ✱ (3 per shot): shield damage 48, hull damage 14; lifetime 6, velocity 30

## 11. Ion Hail Turret (Turrets)

Reload 15 frames: 4.00 shots/s.

| Damage type | Final submunitions (100%) | **80% per shot** | **80% per second** | Direct hit per shot |
|---|---|---|---|---|
| hull damage | 20 | **16** | **64.0** | 20 |
| shield damage | 48 | **38.4** | **153.6** | 48 |
| hit force | 4 | **3.2** | **12.8** | 4 |
| ion damage | 1.2 | **0.96** | **3.8** | 1.2 |
| scrambling damage | 1.2 | **0.96** | **3.8** | 1.2 |

Submunition chain (own stats; ✱ = final submunition):

- 4 × **ion hail** ✱ (4 per shot): hit force 1, shield damage 12, hull damage 5, ion damage 0.3, scrambling damage 0.3; lifetime 40

## 12. Ka'het Annihilator Turret (Turrets)

Reload 10 frames: 6.00 shots/s.

| Damage type | Final submunitions (100%) | **80% per shot** | **80% per second** | Direct hit per shot |
|---|---|---|---|---|
| hull damage | 24 | **19.2** | **115.2** | 24 |
| shield damage | 86 | **68.8** | **412.8** | 86 |

Submunition chain (own stats; ✱ = final submunition):

- 2 × **Annihilator Projectile** ✱ (2 per shot): shield damage 43, hull damage 12; lifetime 35, velocity 18

## 13. Proton Turret (Turrets)

Reload 8 frames: 7.50 shots/s.

| Damage type | Final submunitions (100%) | **80% per shot** | **80% per second** | Direct hit per shot |
|---|---|---|---|---|
| hull damage | 25.2 | **20.16** | **151.2** | 25.2 |
| shield damage | 30.3 | **24.24** | **181.8** | 30.3 |
| hit force | 27 | **21.6** | **162.0** | 27 |

Submunition chain (own stats; ✱ = final submunition):

- 3 × **Proton Fragment** ✱ (3 per shot): hit force 9, shield damage 10.1, hull damage 8.4; lifetime 24

## 14. Speckle Turret (Turrets)

Reload 18 frames: 3.33 shots/s.

| Damage type | Final submunitions (100%) | **80% per shot** | **80% per second** | Direct hit per shot |
|---|---|---|---|---|
| hull damage | 96 | **76.8** | **256.0** | 96 |
| shield damage | 48 | **38.4** | **128.0** | 48 |
| hit force | 36 | **28.8** | **96.0** | 36 |

Submunition chain (own stats; ✱ = final submunition):

- 1 × **Speck** ✱ (1 per shot): shield damage 24, hull damage 48, hit force 18; lifetime 24, velocity 30
- 1 × **Speck** ✱ (1 per shot): shield damage 24, hull damage 48, hit force 18; lifetime 24, velocity 30

## 15. UREB Turret (Turrets)

Reload 6 frames: 10.00 shots/s.

| Damage type | Final submunitions (100%) | **80% per shot** | **80% per second** | Direct hit per shot |
|---|---|---|---|---|
| hull damage | 27 | **21.6** | **216.0** | 27 |
| shield damage | 21.6 | **17.28** | **172.8** | 21.6 |
| scrambling damage | 0.54 | **0.432** | **4.3** | 0.54 |

Submunition chain (own stats; ✱ = final submunition):

- 180 × **GeV Electron Bunch** ✱ (180 per shot): shield damage 0.12, hull damage 0.15, scrambling damage 0.003; lifetime 12, velocity 300

## 16. Cluster Mine Layer (Secondary Weapons)

Reload 180 frames: 0.33 shots/s.

| Damage type | Final submunitions (100%) | **80% per shot** | **80% per second** | Direct hit per shot |
|---|---|---|---|---|
| hull damage | 3080 | **2464** | **821.3** | 680 |
| shield damage | 3850 | **3080** | **1026.7** | 650 |
| hit force | 3300 | **2640** | **880.0** | 3075 |

Submunition chain (own stats; ✱ = final submunition):

- 11 × **Korath Mine Submunition** ✱ (11 per shot): shield damage 350, hull damage 280, hit force 300; lifetime 1000, velocity 2

## 17. External Launch Tube (Secondary Weapons)

Reload 180 frames: 0.33 shots/s.

| Damage type | Final submunitions (100%) | **80% per shot** | **80% per second** | Direct hit per shot |
|---|---|---|---|---|
| hull damage | 19200 | **15360** | **5120.0** | 19200 |
| shield damage | 12600 | **10080** | **3360.0** | 12600 |
| hit force | 7800 | **6240** | **2080.0** | 7800 |

Submunition chain (own stats; ✱ = final submunition):

- 1 × **Orchid Active** (1 per shot): no damage of its own; lifetime 15
  - 1 × **Orchid Boost** (1 per shot): no damage of its own; lifetime 180
    - 1 × **Orchid Coast** (1 per shot): no damage of its own; lifetime 180
      - 1 × **Orchid Divert** (1 per shot): no damage of its own; lifetime 300
        - 1 × **Orchid Terminal** ✱ (1 per shot): shield damage 12000, hull damage 18000, hit force 6000; lifetime 180, blast radius 180
        - 1 × **Orchid Divert Stage Expended** ✱ (1 per shot): shield damage 300, hull damage 600, hit force 900; lifetime 300, velocity -12
    - 1 × **Orchid Boost Stage Expended** ✱ (1 per shot): shield damage 300, hull damage 600, hit force 900; lifetime 300, velocity -18

## 18. Finisher Maegrolain (Secondary Weapons)

Reload 60 frames: 1.00 shots/s.

| Damage type | Final submunitions (100%) | **80% per shot** | **80% per second** | Direct hit per shot |
|---|---|---|---|---|
| hull damage | 1900 | **1520** | **1520.0** | 1900 |
| shield damage | 1500 | **1200** | **1200.0** | 1500 |
| hit force | 1125 | **900** | **900.0** | 1125 |

Submunition chain (own stats; ✱ = final submunition):

- 1 × **Active Finisher** ✱ (1 per shot): shield damage 1500, hull damage 1900, hit force 1125; lifetime 500

## 19. Finisher Pod (Secondary Weapons)

Reload 80 frames: 0.75 shots/s.

| Damage type | Final submunitions (100%) | **80% per shot** | **80% per second** | Direct hit per shot |
|---|---|---|---|---|
| hull damage | 1900 | **1520** | **1140.0** | 1900 |
| shield damage | 1500 | **1200** | **900.0** | 1500 |
| hit force | 1125 | **900** | **675.0** | 1125 |

Submunition chain (own stats; ✱ = final submunition):

- 1 × **Active Finisher** ✱ (1 per shot): shield damage 1500, hull damage 1900, hit force 1125; lifetime 500

## 20. Firelight Missile Bank (Secondary Weapons)

Reload 120 frames: 0.50 shots/s.

| Damage type | Final submunitions (100%) | **80% per shot** | **80% per second** | Direct hit per shot |
|---|---|---|---|---|
| hull damage | 950 | **760** | **380.0** | 950 |
| shield damage | 950 | **760** | **380.0** | 950 |
| burn damage | 10 | **8** | **4.0** | 10 |
| heat damage | 1800 | **1440** | **720.0** | 1800 |
| hit force | 600 | **480** | **240.0** | 840 |

Submunition chain (own stats; ✱ = final submunition):

- 1 × **Firelight Turning** (1 per shot): hit force 90; lifetime 20, velocity 0.1
  - 1 × **Firelight Activated** ✱ (1 per shot): shield damage 950, hull damage 950, heat damage 1800, burn damage 10, hit force 600; lifetime 168, velocity 3

## 21. Flamethrower (Secondary Weapons)

Reload 1 frames: 60.00 shots/s.

| Damage type | Final submunitions (100%) | **80% per shot** | **80% per second** | Direct hit per shot |
|---|---|---|---|---|
| hull damage | 0.7 | **0.56** | **33.6** | 0.7 |
| shield damage | 0.8 | **0.64** | **38.4** | 0.8 |
| heat damage | 160 | **128** | **7680.0** | 160 |

Submunition chain (own stats; ✱ = final submunition):

- 1 × **Flamethrower Projectile** ✱ (1 per shot): shield damage 0.8, hull damage 0.7, heat damage 160; lifetime 18

## 22. Gatling Gun (Secondary Weapons)

Reload 3 frames: 20.00 shots/s.

| Damage type | Final submunitions (100%) | **80% per shot** | **80% per second** | Direct hit per shot |
|---|---|---|---|---|
| hull damage | 6 | **4.8** | **96.0** | 6 |
| shield damage | 3 | **2.4** | **48.0** | 3 |
| hit force | 3 | **2.4** | **48.0** | 3 |

Submunition chain (own stats; ✱ = final submunition):

- 1 × **gbullet** ✱ (1 per shot): shield damage 3, hull damage 6, hit force 3; lifetime 20

## 23. Gatling Turret (Secondary Weapons)

Reload 3 frames: 20.00 shots/s.

| Damage type | Final submunitions (100%) | **80% per shot** | **80% per second** | Direct hit per shot |
|---|---|---|---|---|
| hull damage | 12 | **9.6** | **192.0** | 12 |
| shield damage | 6 | **4.8** | **96.0** | 6 |
| hit force | 6 | **4.8** | **96.0** | 6 |

Submunition chain (own stats; ✱ = final submunition):

- 1 × **gbullet** ✱ (1 per shot): shield damage 3, hull damage 6, hit force 3; lifetime 20
- 1 × **gbullet** ✱ (1 per shot): shield damage 3, hull damage 6, hit force 3; lifetime 20

## 24. Langrage Hyper-Heaver (Secondary Weapons)

Reload 40 frames: 1.50 shots/s.

| Damage type | Final submunitions (100%) | **80% per shot** | **80% per second** | Direct hit per shot |
|---|---|---|---|---|
| hull damage | 342 | **273.6** | **410.4** | 0 |
| shield damage | 342 | **273.6** | **410.4** | 0 |
| hit force | 603 | **482.4** | **723.6** | 6603 |

Submunition chain (own stats; ✱ = final submunition):

- 20 × **Heaver Shard** (20 per shot): hit force 30; lifetime 20, velocity 10
  - 3 × **Heaver Splinter** ✱ (60 per shot): shield damage 5.7, hull damage 5.7, hit force 10.05; lifetime 20

## 25. Medium VLS (Secondary Weapons)

Reload 15 frames: 4.00 shots/s.

| Damage type | Final submunitions (100%) | **80% per shot** | **80% per second** | Direct hit per shot |
|---|---|---|---|---|
| hull damage | 216 | **172.8** | **691.2** | 108 |
| shield damage | 162 | **129.6** | **518.4** | 81 |
| hit force | 648 | **518.4** | **2073.6** | 648 |

Submunition chain (own stats; ✱ = final submunition):

- 1 × **Nettle Active** (1 per shot): shield damage -81, hull damage -108; lifetime 300
  - 18 × **Nettle Flecks** ✱ (18 per shot): shield damage 9, hull damage 12, hit force 36; lifetime 60

## 26. Railgun (Secondary Weapons)

Reload 12 frames: 5.00 shots/s.

| Damage type | Final submunitions (100%) | **80% per shot** | **80% per second** | Direct hit per shot |
|---|---|---|---|---|
| hull damage | 8.4 | **6.72** | **33.6** | 8.4 |
| shield damage | 4.2 | **3.36** | **16.8** | 4.2 |
| hit force | 22.5 | **18** | **90.0** | 22.5 |
| ion damage | 0.3 | **0.24** | **1.2** | 0.3 |
| scrambling damage | 0.3 | **0.24** | **1.2** | 0.3 |

Submunition chain (own stats; ✱ = final submunition):

- 1 × **rslug** ✱ (1 per shot): shield damage 4.2, hull damage 8.4, ion damage 0.3, scrambling damage 0.3, hit force 22.5; lifetime 49

## 27. Shard Fabricator (Secondary Weapons)

Reload 60 frames: 1.00 shots/s.

| Damage type | Final submunitions (100%) | **80% per shot** | **80% per second** | Direct hit per shot |
|---|---|---|---|---|
| hull damage | 160 | **128** | **128.0** | 160 |
| shield damage | 110 | **88** | **88.0** | 110 |
| hit force | 30 | **24** | **24.0** | 30 |

Submunition chain (own stats; ✱ = final submunition):

- 1 × **Shard inactive** ✱ (1 per shot): hit force 30, shield damage 110, hull damage 160; lifetime 60

## 28. Small VLS (Secondary Weapons)

Reload 30 frames: 2.00 shots/s.

| Damage type | Final submunitions (100%) | **80% per shot** | **80% per second** | Direct hit per shot |
|---|---|---|---|---|
| hull damage | 216 | **172.8** | **345.6** | 108 |
| shield damage | 162 | **129.6** | **259.2** | 81 |
| hit force | 648 | **518.4** | **1036.8** | 648 |

Submunition chain (own stats; ✱ = final submunition):

- 1 × **Nettle Active** (1 per shot): shield damage -81, hull damage -108; lifetime 300
  - 18 × **Nettle Flecks** ✱ (18 per shot): shield damage 9, hull damage 12, hit force 36; lifetime 60

## 29. Star Tail (Secondary Weapons)

Reload 180 frames: 0.33 shots/s.

| Damage type | Final submunitions (100%) | **80% per shot** | **80% per second** | Direct hit per shot |
|---|---|---|---|---|
| hull damage | 430 | **344** | **114.7** | 1290 |
| shield damage | 410 | **328** | **109.3** | 1230 |

Submunition chain (own stats; ✱ = final submunition):

- 1 × **Star Tail Projectile** ✱ (1 per shot): shield damage 410, hull damage 430; lifetime 120, velocity 1

## 30. Thunderhead Launcher (Secondary Weapons)

Reload 75 frames: 0.80 shots/s.

| Damage type | Final submunitions (100%) | **80% per shot** | **80% per second** | Direct hit per shot |
|---|---|---|---|---|
| hull damage | 400 | **320** | **256.0** | 400 |
| shield damage | 550 | **440** | **352.0** | 550 |
| hit force | 1125 | **900** | **720.0** | 1125 |

Submunition chain (own stats; ✱ = final submunition):

- 5 × **Thunderhead** ✱ (5 per shot): shield damage 110, hull damage 80, hit force 225; lifetime 400, velocity 2

## 31. Tiny VLS (Secondary Weapons)

Reload 60 frames: 1.00 shots/s.

| Damage type | Final submunitions (100%) | **80% per shot** | **80% per second** | Direct hit per shot |
|---|---|---|---|---|
| hull damage | 216 | **172.8** | **172.8** | 108 |
| shield damage | 162 | **129.6** | **129.6** | 81 |
| hit force | 648 | **518.4** | **518.4** | 648 |

Submunition chain (own stats; ✱ = final submunition):

- 1 × **Nettle Active** (1 per shot): shield damage -81, hull damage -108; lifetime 300
  - 18 × **Nettle Flecks** ✱ (18 per shot): shield damage 9, hull damage 12, hit force 36; lifetime 60

