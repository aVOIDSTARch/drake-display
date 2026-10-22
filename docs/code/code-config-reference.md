# Config Reference

The model's factors are defined in TOML files in [`configs/`](../../configs/). This guide covers every key, the validation rule for each, and the two config files that ship with Phase 0.

There are two kinds of config document:

| Kind | Loaded by | Builds | Factors carry |
| --- | --- | --- | --- |
| **Log-odds** (the habitability model) | `load_log_odds_field_from_path` | `LogOddsField` | `sign`, `backing`, `magnitude`, `temporal`, `inputs` |
| **Composite** (plain additive fields) | `load_composite_field_from_path` | `CompositeField` | `weight` |

Both kinds share the **spatial keys** (`center`, `kernel`, `distance`) and the same validation style:

- **FATAL:** there is no safe default; the config won't build.
- **CORRECTABLE:** a safe default is applied and reported.

Every issue is printed in one pass, and the loader raises `ConfigValidationError` if any FATAL issue remains. See [`code-fields-reference.md`](code-fields-reference.md#config-validation-fieldsconfig_validation) for the Python API.

---

## A log-odds document

```toml
baseline = -0.51                 # B0, the log-odds with no factors present

[[factor]]
name = "FAC-METAL"
sign = 1                         # +1 raises habitability, -1 lowers it
magnitude = 1.83                 # strength M, >= 0
backing = 0.9                    # science-backing weight w, in [0, 1]
center = [0.0, 0.0, 0.0]         # galactocentric kpc
kernel = { type = "metallicity_band" }
distance = { type = "cylindrical" }
temporal = { type = "static" }
inputs = { r_gal_kpc = 0.85, feh = 0.40 }   # confidence of each entity field it reads

[[factor]]
name = "FAC-SN demo star"
sign = -1
magnitude = 3.7
backing = 0.9
center = [-8.23, 0.0, 0.0]
kernel = { type = "truncated_inverse_square", kill_radius = 0.010 }
distance = { type = "euclidean" }
temporal = { type = "ramp_spike_decay", t_birth_myr = 0.0, mass_msun = 20.0, decay_myr = 2.0 }
inputs = { position = 0.1, mass_msun = 0.1 }
```

Each `[[factor]]` table adds one factor. Its contribution to the log-odds is `sign · backing · magnitude · kernel(distance(point, center)) · temporal(t)`.

### Document keys

| Key | Required | Rule |
| --- | --- | --- |
| `baseline` | no | Missing → **CORRECTABLE**, defaults to 0.0. Not a number → **FATAL** |
| `factor` | — | An array of factor tables. An empty document builds an empty field |

### Log-odds factor keys

| Key | Required | Rule |
| --- | --- | --- |
| `name` | no | Missing → **CORRECTABLE**: a unique `unnamed_factor_N` |
| `sign` | **yes** | Missing → **FATAL**: no safe default direction. Must be `1` or `-1`, and booleans are rejected → otherwise **FATAL** |
| `backing` | **yes** | Missing → **FATAL**: there's no honest default for science confidence. Must be a number in [0, 1] → otherwise **FATAL** |
| `magnitude` | **yes** | Missing → **FATAL**. Must be a number ≥ 0 → otherwise **FATAL** |
| `weight` | **must not appear** | Present → **FATAL**. It's ambiguous in a log-odds factor; split it into sign, backing and magnitude |
| `inputs` | no | Missing → **CORRECTABLE**: `{}`, meaning the factor's confidence assumes the low default (0.10). Each value must be a number in [0, 1] → otherwise **FATAL** |
| `temporal` | no | Missing → **CORRECTABLE**: `{ type = "static" }`. The warning asks you to check the factor really doesn't change over time |
| `center` | **yes** | Missing → **FATAL**: no safe default location |
| `kernel` | **yes** | See [Kernel types](#kernel-types) |
| `distance` | **yes** | See [Distance types](#distance-types) |

## A composite document

```toml
[[factor]]
name = "core"
weight = 2.0
center = [0.0, 0.0]
kernel = { type = "gaussian", sigma = 1.0 }
distance = { type = "euclidean" }
```

| Key | Required | Rule |
| --- | --- | --- |
| `name` | no | Missing → **CORRECTABLE**: `unnamed_factor_N` |
| `weight` | no | Missing → **CORRECTABLE**: 1.0, with a warning to check it's intended |
| `center`, `kernel`, `distance` | **yes** | As for log-odds factors |

---

## Kernel types

`kernel = { type = "<name>", <parameters> }`

| `type` | Required parameters | Optional parameters | Shape |
| --- | --- | --- | --- |
| `gaussian` | `sigma` | — | exp(−r²/2σ²) |
| `inverse_square` | `scale` | — | 1/(1 + (r/scale)²) |
| `compact_support` | `radius` | — | max(0, 1 − r/radius)² |
| `constant` | — | `radius` | 1 everywhere, or 1 inside `radius` |
| `exponential` | `scale` | — | exp(−r/scale) |
| `logistic_step` | `radius`, `width` | — | Smooth step: ~1 inside, 0.5 at `radius`, ~0 outside |
| `metallicity_band` | — | `r_sun_kpc`, `feh_sun`, `gradient`, `feh_opt`, `sigma_low`, `sigma_high` | [Fe/H] gradient → asymmetric band (placeholder EQ-CHEM-3) |
| `truncated_inverse_square` | `kill_radius` | `cutoff_factor` (default 5) | min(1, (kill_radius/r)²), 0 beyond the cutoff |

Missing `type` or an unknown `type` → **FATAL**, with a "did you mean" hint for near misses (e.g. `gausian` → `gaussian`). A missing required parameter → **FATAL**.

## Distance types

`distance = { type = "<name>", <parameters> }`

| `type` | Required parameters | Optional parameters | Measures |
| --- | --- | --- | --- |
| `euclidean` | — | — | Straight-line distance |
| `anisotropic` | `a`, `b` | `angle_rad` | Distance on an ellipse with semi-axes `a`, `b`, rotated by `angle_rad`. 2D only |
| `cylindrical` | — | — | Distance in the x–y plane, ignoring z. Centered on the origin, this is galactocentric radius |
| `disk_scaled` | `h_R`, `h_z` | — | R/h_R + \|z\|/h_z. Use with `exponential`, `scale = 1.0` for disk density |

For `anisotropic`, a missing `angle_rad` → **CORRECTABLE** (0.0, unrotated). Unknown or missing types and missing required parameters → **FATAL**.

## Temporal types

`temporal = { type = "<name>", <parameters> }`

| `type` | Parameters | Behavior |
| --- | --- | --- |
| `static` | — | 1 at all times |
| `ramp_spike_decay` | `t_birth_myr` (required); **exactly one** of `t_collapse_myr` or `mass_msun`; `decay_myr` (optional) | Ramps up as (elapsed fraction)³ toward collapse, reaches 1 at collapse, then decays as exp(−Δt/decay). With `mass_msun`, collapse = birth + 10⁴·M^−2.5 Myr |

For `ramp_spike_decay`:
- A missing `t_birth_myr` → **FATAL**.
- Giving both `t_collapse_myr` and `mass_msun`, or neither → **FATAL**.
- A missing `decay_myr` → **CORRECTABLE** (2.0 Myr).

---

## What validation does not check

Two gaps to know about:

- **Parameter values are not range-checked by the validator.** The kernel, metric and profile constructors check them, and raise `ValueError` when the config is *built*. A `sigma = 0` passes validation and fails at load time. So does a `t_collapse_myr` earlier than `t_birth_myr`.
- **Unknown extra keys are ignored**, with one exception. `metallicity_band` passes all of its keys to the constructor, so a misspelled parameter (`sigma_hgh`) raises `TypeError` at build time.

---

## The shipped configs

### `configs/phase0-galactic.toml`

The three smooth, galaxy-wide factors. `veil.registry.build_fields` loads it. Baseline and magnitudes are **calibrated** (ADR-013); `scripts/calibrate_phase0.py` reproduces them.

| Factor | sign | magnitude | backing | Kernel / distance | inputs |
| --- | --- | --- | --- | --- | --- |
| `FAC-METAL` | +1 | 1.83 | 0.9 | `metallicity_band` / `cylindrical` | `r_gal_kpc` 0.85, `feh` 0.40 |
| `FAC-DENSITY` | −1 | 1.75 | 0.6 | `exponential` (scale 1) / `disk_scaled` (h_R 2.5, h_z 0.3) | `r_gal_kpc` 0.85, `z_gal_kpc` 0.85 |
| `FAC-AGN` | −1 | 2.0 | 0.5 | `logistic_step` (radius 2.5, width 0.3) / `cylindrical` | `r_gal_kpc` 0.85 |

`baseline = -0.51`. All three factors are static and centered on the origin.

### `configs/phase0-local.toml`

Two **hypothetical** massive stars near the Sun, 60 pc apart, for the synthetic compounding demo (`scripts/phase0_static.py`) and the acceptance tests. Its `baseline` is 0.0, because baselines add when fields are combined and the galactic file holds B₀. The real pipeline doesn't use this file: it generates supernova factors from the curated star list instead.

### Changing a shipped value

- **Magnitudes and the baseline are guarded by `tests/test_calibration.py`.** If you change one on purpose, update the targets in ADR-013, rerun `scripts/calibrate_phase0.py`, and update the tests together. Don't change one without the others.
- **`inputs` confidences should match the source field maps** in [`docs/data-sources/`](../data-sources/).
