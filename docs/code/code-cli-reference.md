# Command-Line Reference

How to install the engine, run it, and use the helper scripts. All commands run from the repository root.

---

## Installing

Requires Python 3.11 or later.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt          # pinned versions, for reproducible runs
pip install -e '.[dev,phase0]'           # the project itself, editable, with test and pipeline extras
```

The package is named `drake-display`. It provides two importable packages, `fields` and `veil`.

| Extra | Adds | Needed for |
| --- | --- | --- |
| *(none)* | numpy | The `fields` library alone |
| `render` | matplotlib | `fields.render` (static PNGs) |
| `phase0` | pandas, astropy, plotly, matplotlib | The `veil` pipeline |
| `dev` | pytest | Running the tests |

---

## The pipeline: `python src/main.py`

Equivalent to `python -m veil`. With no options, it does a full run:

1. **Fetches** any missing catalog into `data/raw/` (first run only; about 35 MB).
2. **Ingests** about 120,000 entities and writes `data/processed/entities.csv`.
3. **Checks the frame:** stops with an error unless the Sun lands at R ≈ 8.2 kpc, z ≈ 0.
4. **Builds** the galactic and local fields.
5. **Writes** static PNGs and the interactive page to `output/phase0/`.

A full run takes a few seconds once the data is downloaded.

### Options

| Option | Default | Effect |
| --- | --- | --- |
| `--view {galactic,local,both}` | `both` | Which views to render |
| `--t-end T_END` | `15.0` | Last time on the local view's slider, in Myr from now |
| `--t-step T_STEP` | `0.5` | Slider step, in Myr. The number of frames is `t_end / t_step + 1`; each frame adds about 0.35 MB to the page |
| `--out OUT` | `output/phase0` | Output folder |
| `--no-fetch` | off | Stop with an error, instead of downloading, if a catalog is missing. Use it offline or in CI |
| `--project-hazards` | off | Measure supernova reach in the plane only, so stars far above or below the Sun's plane also show dips. This overstates their reach, and the page says so (ADR-014) |

### Outputs

| File | Written when | What it is |
| --- | --- | --- |
| `output/phase0/veil.html` | always | The interactive page: galactic surface, local surface with time slider, hoverable markers. Self-contained, about 19 MB with the default options. Open it in a browser |
| `output/phase0/galactic.png` | `galactic` or `both` | Static check of the galactic field |
| `output/phase0/local_now.png` | `local` or `both` | Static check of the local field at t = 0, with hazard stars labelled |
| `data/processed/entities.csv` | always | The full entity table, with provenance columns |
| `data/raw/*.csv`, `data/raw/retrieved.json` | first run | Downloaded catalogs and their retrieval dates |

All of these are ignored by git and safe to delete.

### Examples

```bash
python src/main.py                                  # everything, default options
python src/main.py --view local --t-end 20          # just the time-slider view, 0–20 Myr
python src/main.py --project-hazards                # show every nearby star's dip
python src/main.py --no-fetch --out /tmp/veil       # offline, custom output folder
```

---

## Helper scripts

### `python scripts/calibrate_phase0.py`

Solves for the baseline and magnitudes that hit the calibration targets in ADR-013, and prints them alongside H at several radii. It **doesn't edit any files**. Copy the printed values into `configs/phase0-galactic.toml` and `src/veil/registry.py` (`SN_MAGNITUDE`) yourself, then run the tests.

To change the targets, edit `TARGETS` and `SN_TARGET_H` at the top of the script. Then update ADR-013 and `tests/test_calibration.py` to match.

### `python scripts/phase0_static.py`

Renders the **synthetic** two-star demo from `configs/phase0-local.toml` to `output/phase0/`:
- `galactic.png`, overwriting the pipeline's copy with an identical image;
- `local_t*.png` at seven times, showing the dips deepening toward collapse and then recovering.

This is the source of the README's compounding screenshot.

---

## Tests

```bash
pytest                       # everything, about 2 seconds, no network needed
pytest tests/test_calibration.py -v
```

See [`code-testing.md`](code-testing.md).
