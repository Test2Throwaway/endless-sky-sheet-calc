from sheetcalc.availability import load_in_play
from sheetcalc.gamedata import load_outfits, per_second, space

DATA = '''# comment
outfit `1-"Uurau" Betavoltaic Cell`
\tcategory "Power"
\t"outfit space" -10
\t"energy generation" 0.85
\tweapon
\t\t"reload" 5

ship "Not An Outfit"
\t"outfit space" 100

outfit "Small Heat Shunt"
\t"outfit space" -7
\t"cooling" 13.5
'''

IN_PLAY = '''# Outfits in play

## In play, by category

### Power (2)

- 1-"Uurau" Betavoltaic Cell — sold
- Antimatter Power Cell — taken from ships only (flotsam)
- Fission Drive — taken from ships only (plunder, capture), at most 1

## Not in play, by reason

- Korath Heat Shunt — blocked
'''


def test_load_outfits_handles_quotes_and_ignores_other_blocks(tmp_path):
    (tmp_path / "outfits.txt").write_text(DATA, encoding="utf-8")
    outfits = load_outfits(tmp_path)
    assert set(outfits) == {'1-"Uurau" Betavoltaic Cell', "Small Heat Shunt"}
    cell = outfits['1-"Uurau" Betavoltaic Cell']
    assert space(cell) == 10
    assert per_second(cell, "energy generation") == 0.85 * 60
    assert "reload" not in cell  # second-level attributes are not first-level ones
    assert per_second(outfits["Small Heat Shunt"], "cooling") == 810


def test_load_in_play_reads_source_and_limit(tmp_path):
    path = tmp_path / "in-play.md"
    path.write_text(IN_PLAY, encoding="utf-8")
    in_play = load_in_play(path)
    assert set(in_play) == {'1-"Uurau" Betavoltaic Cell', "Antimatter Power Cell", "Fission Drive"}
    assert in_play["Antimatter Power Cell"].source == "taken from ships only (flotsam)"
    assert in_play["Antimatter Power Cell"].max_count is None
    assert in_play["Fission Drive"].source == "taken from ships only (plunder, capture)"
    assert in_play["Fission Drive"].max_count == 1


def test_weapon_sub_block_is_kept(tmp_path):
    (tmp_path / "w.txt").write_text('outfit "Gun"\n\tcategory "Guns"\n\tweapon\n\t\t"reload" 5\n\t\tsafe\n'
                                    '\t\tsubmunition "Bit" 3\n\t\t\tfacing 10\n\t"mass" 2\n', encoding="utf-8")
    gun = load_outfits(tmp_path)["Gun"]
    assert gun["_weapon"] == {"reload": 5., "safe": 1., "submunition": [("Bit", 3.)]}
    assert gun["mass"] == 2.
