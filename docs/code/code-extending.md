# Extending the Engine

Step-by-step recipes for the common changes. Each lists every file you need to touch; most bugs in a change like this come from missing one.

**Before you start:** changes to the *model* (new factors, new equations, changed strengths) are reviewed before they're implemented. Propose them first, as [`CONTRIBUTING.md`](../CONTRIBUTING.md) describes. Pure engineering changes can go straight to a pull request.

**Contents:**
[A new kernel](#a-new-kernel) ·
[A new distance metric](#a-new-distance-metric) ·
[A new time profile](#a-new-time-profile) ·
[A new galaxy-wide factor (config only)](#a-new-galaxy-wide-factor-config-only) ·
[A new entity-driven factor](#a-new-entity-driven-factor) ·
[A new entity field](#a-new-entity-field) ·
[A new data source](#a-new-data-source) ·
[Recalibrating](#recalibrating) ·
[Documentation duties](#documentation-duties)

---

## A new kernel

A kernel maps distances to weights. Example: a Lorentzian, `1 / (1 + (r/γ)²)^p`.

1. **`src/fields/kernels.py`**: subclass `Kernel`.
   - Validate parameters in `__init__` and raise `ValueError` for bad ones.
   - Implement `evaluate(r)` with NumPy operations only, so it works on any array shape.
   - Make sure it can't overflow or divide by zero, including at r = 0 and very large r.
   - Write a docstring giving the formula and when to use it.

   ```python
   class LorentzianKernel(Kernel):
       """kappa(r) = 1 / (1 + (r / gamma)^2)^power"""

       def __init__(self, gamma: float, power: float = 1.0):
           if gamma <= 0 or power <= 0:
               raise ValueError("gamma and power must be positive")
           self.gamma, self.power = gamma, power

       def evaluate(self, r: np.ndarray) -> np.ndarray:
           return (1.0 + (r / self.gamma) ** 2) ** -self.power
   ```

2. **`src/fields/kernels.py`, `KERNEL_REGISTRY`**: add `"lorentzian": LorentzianKernel`. This makes the name valid in configs.
3. **`src/fields/config_validation.py`, `REQUIRED_PARAMS_BY_KERNEL_TYPE`**: add `"lorentzian": ["gamma"]`. List only parameters with no safe default.
4. **`src/fields/config_loader.py`, `KERNEL_BUILDERS`**: add a builder that reads the required parameters with `block[...]` and the optional ones with `block.get(..., default)`.

   **Skip this step and the type passes validation, then fails with a `KeyError` when the config is built.**
5. **`tests/test_kernels.py`**: test known values, edge cases, and invalid parameters.
6. **`tests/test_log_odds_config.py`**: add a test that a config using the new type validates and loads.
7. **Docs**: add a row to the kernel tables in [`code-fields-reference.md`](code-fields-reference.md) and [`code-config-reference.md`](code-config-reference.md).

## A new distance metric

The same shape as a kernel:

1. Subclass `DistanceMetric` in **`src/fields/distance.py`**. Implement `distance(points, center)`: points `(..., D)` → distances `(...)`.
2. Register it in **`DISTANCE_REGISTRY`**.
3. Add its required parameters to **`REQUIRED_PARAMS_BY_DISTANCE_TYPE`**.
4. Add a builder to **`DISTANCE_BUILDERS`**.
5. Write tests and update the docs.

If the metric only makes sense in some dimensions, say so in the docstring. `AnisotropicDistance.from_ellipse` (2D only) is the example to follow.

## A new time profile

1. **`src/fields/temporal.py`**: subclass `TemporalProfile`.
   - `evaluate(t)` must accept a scalar or an array and return values in [0, 1].
   - Use `np.where`, not `if`, so arrays work.
   - Guard against overflow in the branch `np.where` doesn't select: it's still computed. `RampSpikeDecayProfile` clamps with `np.maximum` for this reason.
2. Register it in **`TEMPORAL_REGISTRY`**.
3. **`src/fields/config_validation.py`, `_validate_temporal`**: add rules for its parameters. Pass required parameters to `_check_typed_block`, which flags missing ones as FATAL. Add any cross-parameter rules (like "exactly one of A or B") explicitly, and give safe defaults as CORRECTABLE issues.
4. Add a builder to **`TEMPORAL_BUILDERS`** in **`src/fields/config_loader.py`**.
5. Add tests in **`tests/test_temporal.py`** and **`tests/test_log_odds_config.py`**, then update the docs.

## A new galaxy-wide factor (config only)

If the factor's shape can be built from existing kernels and metrics, **no code is needed**. Add a `[[factor]]` table to **`configs/phase0-galactic.toml`**:

```toml
[[factor]]
name = "FAC-SPIRAL"
sign = -1
magnitude = 0.4
backing = 0.3
center = [0.0, 0.0, 0.0]
kernel = { type = "...", ... }
distance = { type = "...", ... }
temporal = { type = "static" }
inputs = { x_gal_kpc = 0.85, y_gal_kpc = 0.85 }
```

Then:

- Take `sign` and `backing` from [`factors.md`](../model/factors.md). Take `inputs` confidences from the source field maps.
- **Adding a factor changes the calibration.** `tests/test_calibration.py` will probably fail. Recalibrate (below) instead of loosening the tests.

## A new entity-driven factor

For factors generated from entity rows, like one supernova factor per massive star (`FAC-SN`):

1. **`src/veil/registry.py`**: write a function `row → Factor`, modeled on `supernova_factor`.
   - Build the spatial profile from the row's position.
   - Build the time profile from the row's clock fields, if it has one.
   - Fill `input_confidences` from the row's `F__conf` columns, **never with hard-coded numbers**. This is what keeps confidence honest.
   - Put the factor's constants (sign, backing, magnitude) at the top of the module, each with a comment saying where it comes from.
2. Add a `build_<name>_field(entities)` function that selects the relevant `kind` and returns a `LogOddsField` with baseline 0.
3. Include it in **`build_fields`** through `LogOddsField.combine`. Point factors belong only in the **local** field (ADR-004).
4. Add tests to **`tests/test_veil_pipeline.py`** using the `paths` fixture.

## A new entity field

1. **`docs/model/entity.md`**: add the field first. The schema only grows, so never remove or rename an existing field.
2. **`src/veil/ingest.py`**:
   - Add the field to `PHYSICAL_FIELDS`. Identity-only fields go in `IDENTITY_COLUMNS` instead, and carry no provenance.
   - Fill it in the relevant loader.
   - Add `(tier, confidence)` to the source's field map, so it gets provenance.

   If you forget the field-map entry, the fail-safe still marks the value Speculative/0.10. That's safe but wrong, so add the entry.
3. **Tests**: `test_every_present_physical_value_has_provenance` covers the new field automatically. Add a test for how its value is derived.

## A new data source

1. **Describe it first**: write `docs/data-sources/source-<name>.md` following [`data-source-info-schema.md`](../schemas/data-source-info-schema.md). Include the column → field map with a `(tier, confidence)` for each field, plus the filters and unit fixes.
2. **`src/veil/fetch.py`**: add the file name and URL to `SOURCES`. Keep downloads static and record the retrieval date; don't add live queries at run time.
3. **`src/veil/ingest.py`**:
   - Add a `<NAME>_FIELD_MAP` copied from the description.
   - Write a `load_<name>(path)` that applies the filters and unit fixes, calls `_add_positions` (never the catalog's own Cartesian columns), and finishes with `attach_provenance`.
   - Concatenate its result in `load_entities`.
4. **`src/veil/main.py`**: pass the new path to `load_entities`.
5. **Tests**: add a few representative rows to the `paths` fixture, covering at least one good row and one row that should be filtered out.
6. **Credit**: credit the source under its own terms in [`AUTHORS.md`](../project/AUTHORS.md), "Data sources".

Phase 0 doesn't merge the same object across sources (entity resolution). If your source overlaps an existing one, keep separate rows for now and note it. Resolution is planned for Phase 3 (ADR-012).

## Recalibrating

Do this after changing factors or targets:

1. Edit `TARGETS` / `SN_TARGET_H` in **`scripts/calibrate_phase0.py`** if the targets changed. If the factor set changed, update its column construction too.
2. Run `python scripts/calibrate_phase0.py` and copy the values into **`configs/phase0-galactic.toml`** and **`src/veil/registry.py`**.
3. Update **ADR-013** in [`DECISIONS.md`](../project/DECISIONS.md) and the targets in **`tests/test_calibration.py`**, together.
4. Regenerate the README screenshots: run `python src/main.py` and `python scripts/phase0_static.py`, then copy the PNGs into `docs/images/phase0/`.

## Documentation duties

Every change that adds or renames something should also:

- **Update the matching guide** in `docs/code/`.
- **Register any new document** in the document manifest, [`docs/documents.toml`](../documents.toml). The manifest test fails until you do. See [`schema-document-descriptor.md`](../schemas/schema-document-descriptor.md).
- **Record structural decisions** as a new ADR in [`DECISIONS.md`](../project/DECISIONS.md).
- **Add a line to the changelog** in [`CHANGELOG.md`](../project/CHANGELOG.md).
