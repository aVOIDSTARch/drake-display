# `fields` Reference

API reference for `src/fields/`, the general library for scalar fields over space and time. For how the pieces fit together, read [`code-architecture.md`](code-architecture.md) first.

Throughout, **points** are arrays of shape `(..., D)`, a **center** has shape `(D,)`, and functions return one value per point, shape `(...)`.

**Contents:**
[Kernels](#kernels-fieldskernels) ·
[Distance metrics](#distance-metrics-fieldsdistance) ·
[SourceField](#sourcefield-fieldssource_field) ·
[CompositeField](#compositefield-fieldscomposite_field) ·
[Time profiles](#time-profiles-fieldstemporal) ·
[Factor](#factor-fieldsfactor) ·
[LogOddsField](#logoddsfield-fieldslog_odds_field) ·
[Grids](#grids-fieldsgrid) ·
[Config validation](#config-validation-fieldsconfig_validation) ·
[Config loading](#config-loading-fieldsconfig_loader) ·
[Rendering](#rendering-fieldsrender)

---

## Kernels (`fields.kernels`)

A kernel turns distances into falloff weights. It knows nothing about geometry; it transforms whatever array of distances it's given.

### `Kernel` (abstract)

| Member | Description |
| --- | --- |
| `evaluate(r) -> ndarray` | **Abstract.** Map an array of non-negative distances to a same-shape array of weights |
| `__call__(r)` | Same as `evaluate(r)` |

### Built-in kernels

| Class | Config name | Formula | Parameters |
| --- | --- | --- | --- |
| `GaussianKernel` | `gaussian` | exp(−r² / 2σ²) | `sigma` > 0 |
| `InverseSquareKernel` | `inverse_square` | 1 / (1 + (r/scale)²) | `scale` > 0 (default 1.0) |
| `CompactSupportKernel` | `compact_support` | max(0, 1 − r/R)²; exactly 0 beyond R | `radius` > 0 |
| `ConstantKernel` | `constant` | 1 everywhere, or 1 inside `radius` and 0 outside | `radius` (optional; `None` = everywhere) |
| `ExponentialKernel` | `exponential` | exp(−r / scale) | `scale` > 0 (default 1.0) |
| `LogisticStepKernel` | `logistic_step` | 1 / (1 + e^((r − radius)/width)): ~1 inside, 0.5 at `radius`, ~0 outside | `radius` > 0, `width` > 0 |
| `MetallicityBandKernel` | `metallicity_band` | See below | All optional; defaults from `factors.md` Appendix A |
| `TruncatedInverseSquareKernel` | `truncated_inverse_square` | min(1, (kill_radius / r)²), and 0 beyond `cutoff_factor · kill_radius` | `kill_radius` > 0, `cutoff_factor` ≥ 1 (default 5) |

Constructors raise `ValueError` for non-positive scale parameters.

**`MetallicityBandKernel`** is the FAC-METAL spatial profile. It expects `r` to be galactocentric cylindrical radius in kpc, so pair it with `CylindricalDistance` centered on the origin. It works in two steps:

1. `feh(r) = feh_sun + gradient · (r − r_sun_kpc)`. This is EQ-CHEM-1, an established gradient. `feh(r)` is also a public method.
2. An asymmetric Gaussian in [Fe/H] peaking at 1 at `feh_opt`, with width `sigma_low` below the peak and `sigma_high` above. This is a **placeholder** for EQ-CHEM-3.

| Parameter | Default |
| --- | --- |
| `r_sun_kpc` | 8.2 |
| `feh_sun` | 0.0 |
| `gradient` | −0.06 dex/kpc |
| `feh_opt` | 0.0 |
| `sigma_low` | 0.3 |
| `sigma_high` | 0.6 |

**`TruncatedInverseSquareKernel`** is P-POINT, the supernova profile: full strength inside the kill radius, inverse-square fade outside it, and a hard edge. At the default cutoff the falloff has only reached 1/25 when it drops to 0.

**`KERNEL_REGISTRY`** maps each config name to its class.

---

## Distance metrics (`fields.distance`)

A metric turns points and a center into one distance per point.

### `DistanceMetric` (abstract)

| Member | Description |
| --- | --- |
| `distance(points, center) -> ndarray` | **Abstract.** Points `(..., D)`, center `(D,)` → distances `(...)` |
| `__call__(points, center)` | Same as `distance` |

### Built-in metrics

| Class | Config name | Distance | Parameters |
| --- | --- | --- | --- |
| `EuclideanDistance` | `euclidean` | Straight line | — |
| `AnisotropicDistance` | `anisotropic` | √((p−c)ᵀ A (p−c)). Ellipses at any angle | `A`: a symmetric positive-definite matrix |
| `CylindricalDistance` | `cylindrical` | √(dx² + dy²); ignores z. Centered on the origin, this is galactocentric radius R | — |
| `DiskScaledDistance` | `disk_scaled` | R/h_R + \|z\|/h_z. With `ExponentialKernel(scale=1)` this gives exactly the disk density of EQ-PROF-1 | `h_R` > 0, `h_z` > 0 |

`AnisotropicDistance.from_ellipse(a, b, angle_rad=0.0)` builds a 2D ellipse metric from its semi-axes `a` and `b` (both > 0) and a counter-clockwise rotation. It raises `ValueError` for non-positive axes. In config files, `anisotropic` takes `a`, `b` and optionally `angle_rad`, not a raw matrix.

For 2D points, `CylindricalDistance` equals `EuclideanDistance`, and `DiskScaledDistance` treats height as 0.

**`DISTANCE_REGISTRY`** maps each config name to its class.

---

## `SourceField` (`fields.source_field`)

A single spatial influence: `weight · kernel(distance_metric(points, center))`.

```python
SourceField(distance_metric, kernel, center, weight=1.0, name=None)
```

| Parameter | Description |
| --- | --- |
| `distance_metric` | A `DistanceMetric` |
| `kernel` | A `Kernel` |
| `center` | The source position, shape `(D,)`; converted to a float array |
| `weight` | Scalar multiplier. Use 1.0 when the field is a `Factor`'s spatial profile, since the factor carries strength separately |
| `name` | Optional. If omitted, a unique `unnamed_factor_N` is assigned |

Call it as `field(points)` or `field.evaluate(points)`; both return shape `(...)`.

---

## `CompositeField` (`fields.composite_field`)

The plain, linear sum of several source fields.

```python
CompositeField(source_fields)        # list of SourceField (or any callable points -> values)
composite(points)                    # sum of each source's values, shape (...)
```

An empty list gives zeros. Use `LogOddsField` for the habitability model. `CompositeField` remains for raw additive fields.

---

## Time profiles (`fields.temporal`)

A time profile `g(t)` scales a factor's strength over time. Values are in [0, 1]; `t` is in Myr and may be a scalar or an array.

### `TemporalProfile` (abstract)

| Member | Description |
| --- | --- |
| `evaluate(t) -> ndarray` | **Abstract.** Same shape as `t` |
| `__call__(t)` | Same as `evaluate(t)` |

### `StaticProfile`

G-STATIC: `g(t) = 1` always. Config name `static`. The default for every factor.

### `RampSpikeDecayProfile`

G-RAMP-SPIKE-DECAY: the hazard clock for a massive star. Config name `ramp_spike_decay`.

```python
RampSpikeDecayProfile(t_birth_myr, t_collapse_myr, decay_myr=2.0)
RampSpikeDecayProfile.from_mass(t_birth_myr, mass_msun, decay_myr=2.0)
```

```text
t <  t_collapse:  ((t − t_birth) / (t_collapse − t_birth))³, clipped to [0, 1]
t >= t_collapse:  exp(−(t − t_collapse) / decay_myr)
```

The profile is negligible early, rises to exactly 1 at collapse, then decays as the remnant fades. `from_mass` sets `t_collapse = t_birth + ms_lifetime_myr(mass_msun)`.

The constructor raises `ValueError` if `t_collapse_myr ≤ t_birth_myr` or `decay_myr ≤ 0`.

### Helpers

| Name | Description |
| --- | --- |
| `ms_lifetime_myr(mass_msun)` | EQ-STAR-1: `1e4 · mass^−2.5` Myr. A 20 M☉ star gives about 5.6 Myr. Raises `ValueError` for non-positive mass |
| `MS_LIFETIME_NORM_MYR` | 1.0 × 10⁴ |
| `TEMPORAL_REGISTRY` | Config name → class |

---

## `Factor` (`fields.factor`)

One term of the log-odds sum.

```python
Factor(name, spatial, sign, backing, magnitude,
       temporal=StaticProfile(), input_confidences={})
```

| Field | Type | Description |
| --- | --- | --- |
| `name` | `str` | Identifier, e.g. `"FAC-METAL"` |
| `spatial` | callable `points -> (...)` | The spatial profile `f`, normally a `SourceField` with `weight=1.0`. Values in [0, 1] |
| `sign` | `int` | +1 raises habitability, −1 lowers it. Optimum-band factors use +1 with a band-shaped profile |
| `backing` | `float` in [0, 1] | Science-backing weight `w` |
| `magnitude` | `float` ≥ 0 | Strength `M` |
| `temporal` | `TemporalProfile` | `g(t)`; defaults to static |
| `input_confidences` | `Mapping[str, float]` | Confidence (0–1) of each entity field the factor reads, e.g. `{"feh": 0.40}` |

Invalid values raise `ValueError` on construction.

| Member | Description |
| --- | --- |
| `contribution(points, t) -> ndarray` | `sign · backing · magnitude · spatial(points) · temporal(t)`, shape `(...)` |
| `confidence` (property) | EQ-CORE-4 steps 1–2: `backing × min(input_confidences)`. With no inputs declared, `backing × DEFAULT_FIELD_CONFIDENCE` |

`DEFAULT_FIELD_CONFIDENCE = 0.10` is the project-wide confidence assumed for any value nobody vouched for. `veil.ingest` reuses it.

---

## `LogOddsField` (`fields.log_odds_field`)

Sums factors in log-odds space and returns habitability and confidence from one pass.

```python
field = LogOddsField(factors, baseline=0.0)
sample = field(points, t)            # or field.evaluate(points, t)
```

`sample` is a **`VeilSample`**. Every array in it has shape `points.shape[:-1]`.

| Field | Description |
| --- | --- |
| `height` | H in [0, 1]: `logistic(logit)` |
| `confidence` | EQ-CORE-4: `Σ cᵢ·\|ℓᵢ\| / Σ \|ℓᵢ\|`; `NO_CONTRIBUTION_CONFIDENCE` (0.0) where no factor contributes |
| `logit` | `baseline + Σ contributions`, before the logistic |

| Member | Description |
| --- | --- |
| `factors`, `baseline` | The terms and B₀ |
| `LogOddsField.combine(fields)` | One field with every input's factors and the **sum** of their baselines. Logits add, so this is exact. Used to put point hazards on top of the galactic field |
| `logistic(x)` (module function) | A numerically stable 1/(1+e^−x), computed as `0.5·(1 + tanh(x/2))` so it never overflows |

`t` is a scalar time in Myr. To animate, call the field once per time step.

---

## Grids (`fields.grid`)

```python
make_grid(kind, center=(0.0, 0.0, 0.0), spec=None) -> Grid
```

Builds a square patch of the plane z = `center[2]`. `kind` is `"galactic"` or `"local"` (from `GRID_SPECS`), or any label if you pass `spec`. Unknown kinds without a `spec` raise `ValueError`.

| `GRID_SPECS` entry | Half-width | Cells | Resolution |
| --- | --- | --- | --- |
| `galactic` | 20 kpc | 300 × 300 | ~130 pc |
| `local` | 0.2 kpc | 200 × 200 | ~2 pc |

**`GridSpec(half_width_kpc, cells)`** is frozen. It requires a positive half-width and at least 2 cells.

**`Grid`** fields:

| Field | Shape | Description |
| --- | --- | --- |
| `kind` | — | The label |
| `x`, `y` | `(nx,)`, `(ny,)` | Axis coordinates |
| `X`, `Y` | `(ny, nx)` | Meshgrids, for plotting |
| `points` | `(ny, nx, 3)` | Points to evaluate fields on |
| `R` (property) | `(ny, nx)` | Galactocentric cylindrical radius per cell |
| `extent` (property) | — | `(xmin, xmax, ymin, ymax)`, as `imshow` wants it |

---

## Config validation (`fields.config_validation`)

Checks parsed TOML (a `dict`) before anything is built. It never mutates its input and never stops at the first problem. The rules for every key are in [`code-config-reference.md`](code-config-reference.md).

| Function | Validates |
| --- | --- |
| `validate_document(toml_dict, auto_correct=True)` | A composite document (factors with `weight`) |
| `validate_log_odds_document(toml_dict, auto_correct=True)` | A log-odds document (factors with `sign`, `backing`, `magnitude`, …, plus `baseline`) |
| `validate_factor(raw, pos_num, auto_correct=True)` | One composite factor → `(issues, corrected_dict)` |
| `validate_log_odds_factor(raw, pos_num, auto_correct=True)` | One log-odds factor → `(issues, corrected_dict)` |

Both document functions return a **`ValidationReport`**:

| Field | Description |
| --- | --- |
| `is_buildable` | `True` only if there are no FATAL issues and every CORRECTABLE issue was applied |
| `issues` | A list of `Issue` |
| `corrected_factors` | Copies of the factor dicts with corrections applied |
| `baseline` | The (possibly defaulted) baseline. Log-odds documents only |

Each **`Issue`** has these fields:

| Field | Description |
| --- | --- |
| `identifier` | Which factor, e.g. `factor_at_pos_2: FAC-AGN`, or `document` |
| `severity` | `FATAL` or `CORRECTABLE` |
| `field` | The key at fault, e.g. `kernel.sigma` |
| `found_value` | The value found. The sentinel `MISSING` means the key was absent |
| `corrected_value` | The default applied, if any |
| `applied` | Whether the correction was applied |
| `message` | A human-readable explanation, with a "did you mean" hint for typos in type names |

With `auto_correct=False`, CORRECTABLE issues are reported but not applied, so the document is not buildable.

---

## Config loading (`fields.config_loader`)

```python
load_composite_field_from_path(path, auto_correct=True) -> CompositeField
load_log_odds_field_from_path(path, auto_correct=True) -> LogOddsField
```

Each loader:

1. Reads the TOML file.
2. Validates it.
3. Prints every issue as `[SEVERITY] identifier -- field: message`.
4. If the report isn't buildable, raises **`ConfigValidationError`**. The full report is on its `.report` attribute.
5. Otherwise builds the objects.

Log-odds factors get a `SourceField` with `weight=1.0` as their spatial profile.

The builder tables `KERNEL_BUILDERS`, `DISTANCE_BUILDERS` and `TEMPORAL_BUILDERS` map config names to constructors. Every name in a registry needs a builder here; see [`code-extending.md`](code-extending.md).

---

## Rendering (`fields.render`)

Static matplotlib images for checking results by eye. Requires the `render` or `phase0` extra. The backend is forced to `Agg`, so no display is needed.

```python
static_validate(sample, grid, title, out_path, markers=None)
```

Writes a PNG with three panels: H as a heatmap, confidence as a heatmap (red = low, blue = high, both on a 0–1 scale), and H as a 3D surface. **`Marker(x, y, label)`** adds a labelled star to both heatmaps.

The 3D panel's vertical axis scales to the data, so small dips look exaggerated. Read values from the heatmaps.
