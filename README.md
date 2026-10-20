# Endless Sky sheet calc

Tools for working out what ship outfits *really* cost once their supporting outfits are counted:
the cooling for their heat and the generators (plus those generators' cooling) for their energy.

- `legacy/`: the original hand-built spreadsheets.
- `data/outfits-in-play.md`: which outfits a player can actually get. Outfits not listed here are ignored.
- `sheetcalc/`: Python package (needs numpy).
- `tests/`: pytest tests, using small inline data rather than the game files.
- `reports/`: generated output.

## Setup

Needs Python 3.11 or newer and a checkout of the game's source next to this repo (`../endless-sky`), since
`data/outfits-in-play.md` is generated from the current game data:

```
python3 -m venv .venv && . .venv/bin/activate
pip install -e '.[dev]'     # editable, so default paths resolve to this repo
git clone --depth 1 https://github.com/endless-sky/endless-sky.git ../endless-sky
python -m pytest -q
```

## Usage

```
sheetcalc                   # or: python -m sheetcalc
sheetcalc --data PATH/TO/endless-sky/data --in-play data/outfits-in-play.md
```

This writes:

- `reports/cooling_ladder.md`: the least space of whole passive coolers that gives each amount of
  cooling, the coolers it makes obsolete, and the heat price (space per heat/s) by ship heat band.
- `reports/power_plant.md`: generators, passive and active cooling searched together (active coolers
  draw energy, generators make heat), with total plant space by energy and heat load and the resulting
  energy and heat prices for reference ship sizes. Takes a couple of minutes.
- `reports/energy_ladder.md`: the same for energy generation, counting each generator's own cooling,
  and the energy price (space per energy/s) by ship energy band.
- `reports/obsolescence.md`: which generators and coolers are ever needed (strictly dominated, off the passive
  ladder, never in a best power plant, or replaceable by ties), with what each kept one saves and the other stats
  of obsolete ones (batteries, resistances...).
- `reports/core_outfits.json`: the kept outfits per family, plus obsolete-for-power outfits that have other stats.

A full run takes about 6 minutes, most of it the obsolescence analysis.

## Pruning (MVP)

```
sheetcalc-prune                       # or: python -m sheetcalc.prune; all solar cases, all cores
```

Strict dominance plus the power and cooling search per solar case, written to `reports/pruned.json` (for the
optimizer) and `reports/pruned.md`. For a request in solar case S, skip every outfit under `strict` plus every
outfit under `power/S`. About a minute on 4 cores. Design and plans: `docs/pruner-design.md`.

## Obsolescence passes

```
sheetcalc-passes                      # or: python -m sheetcalc.passes; all cases, all cores
sheetcalc-passes --solar none,median --availability sold --jobs 4
```

Runs one obsolescence pass per combination of design options (for power: solar case × availability tier) in
parallel, and writes `reports/passes.json` (for the optimizer) and `reports/passes.md`. See `docs/passes.md` for the
pass catalogue, the output format and why families of outfits can be pruned independently.
