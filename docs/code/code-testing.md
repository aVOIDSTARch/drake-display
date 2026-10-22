# Testing Guide

How the test suite is organized, what it guarantees, and how to add to it.

```bash
pytest                    # the whole suite: about 120 tests, about 2 seconds
pytest -q tests/test_kernels.py
pytest -k calibration -v
```

`pyproject.toml` puts `src/` on the import path and sets `tests/` as the test root, so `pytest` works from the repository root without an install. Installing with `pip install -e '.[dev,phase0]'` gives you every test dependency.

**The suite never touches the network or the downloaded catalogs.** Pipeline tests use small inline CSV fixtures, so it runs the same on a fresh clone, offline, or in CI.

---

## What each file covers

### The `fields` library

| File | Covers |
| --- | --- |
| `test_kernels.py` | Kernel formulas, edge behavior (compact support is exactly 0 beyond R), rejection of bad parameters |
| `test_galactic_profiles.py` | Cylindrical and disk-scaled distances, the disk-density formula (EQ-PROF-1), logistic step, metallicity band, point-hazard kernel |
| `test_source_field.py` | `SourceField` values, grid shapes, unique fallback names |
| `test_composite_field.py` | `CompositeField` is the elementwise sum |
| `test_temporal.py` | Main-sequence lifetime, the static profile, the ramp–spike–decay clock (monotonic ramp, 1 at collapse, decay after), invalid clocks |
| `test_factor.py` | A factor's contribution formula, confidence as backing × weakest input, the 0.10 default, validation |
| `test_log_odds_field.py` | Stable logistic, baseline-only fields, H staying in [0, 1] under extreme stacking, compounding, the confidence channel, `combine` |
| `test_grid.py` | Grid shapes and extents, local-grid resolution against the kill radius |
| `test_render.py` | `static_validate` writes a valid PNG |

### Configs

| File | Covers |
| --- | --- |
| `test_config_validation.py` | Composite documents. Includes the regression test for a bug that once overwrote every factor's `angle_rad` |
| `test_config_loader.py` | Composite TOML → `CompositeField`; a bad file raises with the full report |
| `test_log_odds_config.py` | Every log-odds rule: FATAL strength terms, rejected `weight`, CORRECTABLE defaults, clock rules, the shipped Phase 0 config building |

### The `veil` pipeline

| File | Covers |
| --- | --- |
| `test_veil_pipeline.py` | Coordinates (the Sun at R₀, the galactic center at the origin), star classification, HYG filtering and derived values, hazard joins and clock checks, exoplanet splitting and habitable-zone logic, **per-field provenance and the Speculative/0.10 fail-safe**, slice vs projection |
| `test_veil_render.py` | Animation frames and the fixed H axis, hover text showing provenance, `write_html` inlining plotly once, **no autoplay**, the intro's geometry note, `check_sun` |

### Acceptance and calibration

These two files guard the model's *behavior*, not just the code.

| File | Covers |
| --- | --- |
| `test_phase0_acceptance.py` | The Phase 0 sanity checks from spec §6.11, run on the real configs: H is a valid probability everywhere; the solar band clearly beats the inner galaxy; overlapping hazards compound; a star's dip deepens up to collapse and then recovers |
| `test_calibration.py` | The ADR-013 targets: H ≈ 0.20 at the center, ≈ 0.75 at the Sun's radius (and that's the peak), ≈ 0.40 at 20 kpc; a monotonic rise from center to Sun; a supernova at collapse reaching H ≤ 0.10 |

If one of these fails after a change, the model's behavior changed, not just the code. Fix the change, or, if the new behavior is intended, update the targets and the matching ADR deliberately, in the same commit.

---

## Fixtures and patterns

- **`paths`** (in `test_veil_pipeline.py`) writes tiny HYG, hazard and exoplanet CSVs to a temporary folder and returns them as a `{"hyg", "hazards", "exoplanets"}` dict, ready for `load_entities`. The rows are chosen to hit each case:
  - the Sun;
  - Betelgeuse (a supergiant) and Spica (main sequence);
  - an unknown distance and a missing distance;
  - a giant and a dwarf;
  - a host with two planets, a host with no measured metallicity, and a host with no distance.

  `test_veil_render.py` imports it.
- **Optional dependencies** are guarded with `pytest.importorskip`, so `fields` tests still run in an environment with only numpy.
- **Configs are found relative to the test file** (`Path(__file__).parent.parent / "configs"`), so tests pass from any working directory.
- **Assert on values, not printouts.** Compare arrays with `np.testing.assert_allclose`, and use `pytest.approx` for single numbers.

---

## Adding tests

- **New code in `fields`:** add tests to the matching file, or a new `test_<module>.py`. Cover the formula at a few known points, the shape contract `(..., D) → (...)`, and invalid inputs.
- **New code in `veil`:** extend the `paths` fixture if you need new rows, and keep it small and offline.
- **A new kernel, metric or time profile:** also add a config test showing it validates and loads by name. See the checklist in [`code-extending.md`](code-extending.md).
- **A bug fix:** add a test that fails on the old code. Check it does by running it against the old code before you commit.
