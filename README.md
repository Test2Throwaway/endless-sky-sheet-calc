# Endless Sky sheet calc

Tools for working out what ship outfits *really* cost once their supporting outfits are counted:
the cooling for their heat and the generators (plus those generators' cooling) for their energy.

- `legacy/`: the original hand-built spreadsheets.
- `data/outfits-in-play.md`: which outfits a player can actually get. Outfits not listed here are ignored.
- `sheetcalc/`: Python package (standard library only).
- `reports/`: generated output.

## Usage

```
python -m sheetcalc            # reads ../endless-sky/data by default
python -m sheetcalc --data PATH/TO/endless-sky/data --in-play data/outfits-in-play.md
```

This writes:

- `reports/cooling_ladder.md`: the least space of whole passive coolers that gives each amount of
  cooling, the coolers it makes obsolete, and the heat price (space per heat/s) by ship heat band.
- `reports/energy_ladder.md`: the same for energy generation, counting each generator's own cooling,
  and the energy price (space per energy/s) by ship energy band.
