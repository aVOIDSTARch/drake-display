# `veil` Reference

API reference for `src/veil/`, the Phase 0 pipeline that applies the `fields` library to the galaxy. For the overall flow, read [`code-architecture.md`](code-architecture.md) first. For the command line, see [`code-cli-reference.md`](code-cli-reference.md).

`veil` needs the `phase0` extra (pandas, astropy, scipy, plotly, matplotlib): `pip install -e '.[phase0]'`.

**Contents:**
[fetch](#fetch-veilfetch) ·
[coords](#coords-veilcoords) ·
[ingest](#ingest-veilingest) ·
[The entity table](#the-entity-table) ·
[registry](#registry-veilregistry) ·
[interactive](#interactive-veilinteractive) ·
[main](#main-veilmain)

---

## fetch (`veil.fetch`)

Downloads the raw catalogs that are missing.

```python
fetch_missing(raw_dir: Path) -> list[str]     # names of the files it downloaded
```

- **Never re-downloads.** To refresh a file, delete it and run again.
- **Downloads are atomic.** Each file is written to `<name>.part` and renamed only when complete, so an interrupted download never leaves a truncated catalog.
- **Retrieval is logged.** Each download records its URL and UTC time in `raw_dir/retrieved.json`. The exoplanet archive changes continuously, so that date is what makes a run reproducible.

| Constant | Value |
| --- | --- |
| `HYG_FILE`, `HYG_URL` | `hygdata_v41.csv`, from the astronexus/HYG-Database GitHub repository |
| `EXOPLANET_FILE`, `EXOPLANET_URL` | `exoplanets_ps.csv`, a TAP query on the NASA Exoplanet Archive `ps` table with `default_flag=1` (one row per planet) |
| `EXOPLANET_COLUMNS` | The archive columns requested, per [`source-nasa-exoplanet-archive.md`](../data-sources/source-nasa-exoplanet-archive.md) |
| `WR_FILE`, `WR_URL` | `wolf_rayet_rate_crowther_2020.csv`, a VizieR TAP query on `J/MNRAS/493/1512/table1` ([source](../data-sources/source-galactic-wr-catalogue.md)) |
| `OB_FILE`, `OB_URL` | `als_iii_ob_stars.csv`, a VizieR TAP query on `J/MNRAS/504/2968/tablea1` ([source](../data-sources/source-als-iii.md)) |
| `vizier_url(query)` | Builds a VizieR TAP synchronous CSV query URL |
| `SOURCES` | File name → URL |
| `RETRIEVAL_LOG` | `retrieved.json` |

---

## coords (`veil.coords`)

EQ-GEO-2: ICRS → galactocentric Cartesian.

```python
to_galactocentric(ra_deg, dec_deg, dist_pc) -> (x, y, z)    # arrays, kpc
```

Inputs are equal-length array-likes. The function is vectorized through astropy's `SkyCoord`.

| Constant | Value |
| --- | --- |
| `R0_KPC` | 8.2. The Sun's distance from the galactic center (`factors.md` Appendix A) |
| `Z0_PC` | 20.0. The Sun's height above the plane |
| `GALACTOCENTRIC_FRAME` | astropy `Galactocentric` with those two values |

The Sun comes out at about (−8.2, 0, +0.020) kpc. Its in-plane radius is √(8.2² − 0.02²) = 8.19998 kpc, because astropy's distance is measured in 3D.

---

## ingest (`veil.ingest`)

Raw catalogs → one entity table, following the field maps in [`docs/data-sources/`](../data-sources/).

### Loaders

| Function | Returns |
| --- | --- |
| `load_hyg(path)` | HYG stars, with provenance |
| `load_hazards(path, stars)` | Curated massive stars as `star_massive_progenitor` rows, positioned from their HYG rows |
| `load_wolf_rayet(path)` | Galactic Wolf-Rayet stars as `star_wolf_rayet` rows, with a typical progenitor mass and a statistical collapse time within 0.5 Myr |
| `load_ob_stars(path)` | ALS III O and B stars whose estimated mass is at least 8 M☉, as `star_massive_progenitor` rows, with a statistical collapse time |
| `load_exoplanets(path)` | `planetary_system` rows (one per host) and planet rows, with provenance |
| `load_entities(paths)` | All of the above, unified. `paths` has the keys `"hyg"`, `"exoplanets"` and `"hazards"`, and optionally `"wolf_rayet"` and `"ob_stars"`. Massive stars listed by more than one source are kept once, preferring curated > Wolf-Rayet > ALS III > HYG |

**`load_hyg`**:
- **Filtering:**
  - Drops rows whose distance is missing, non-positive, or HYG's unknown-distance placeholder (100000 pc).
  - Keeps the Sun (`hyg:0`, distance 0) as the reference point.
- **Conversion:** HYG's `ra` is in **hours**, so it's multiplied by 15.
- **Derived values:**
  - Luminosity comes from absolute magnitude: `10^(0.4 · (4.83 − M_V))`.
  - Teff comes from B−V, using the Ballesteros (2012) formula.
  - Mass uses the main-sequence relation `L^(1/3.5)`, for main-sequence stars only; other stars get `NaN`.
  - [Fe/H] is modeled from radius by EQ-CHEM-1.
- **Never** uses HYG's own x/y/z columns (ADR-003).

**`load_hazards`** reads `data/curated/phase0_hazard_stars.csv`, where `#` lines are comments.
- **Join:** each star is matched to its HYG row by Hipparcos number (`hip`), and takes position and photometry from HYG. Mass and collapse time come from the curated file. It then derives:
  - `main_sequence_lifetime_myr` = `ms_lifetime_myr(mass)`;
  - `t_birth_myr` = `t_collapse_myr − lifetime`.
- **Raises `ValueError`:**
  - if a star has no usable HYG row;
  - if a star's collapse time is later than its lifetime allows, which would mean it is born in the future.
- **After loading:** `load_entities` drops the matching HYG rows, so each star appears once and keeps its `hyg:` id.

**`load_exoplanets`**:
- **Filtering:** drops rows without ra, dec or a positive distance.
- **Insolation:** comes from `pl_insol`. Where that's missing, it's computed with EQ-HZ-1 as `10^st_lum / a²`; the archive gives `st_lum` as log₁₀.
- **Habitable zone:** `in_habitable_zone` means insolation between 0.35 and 1.1 S⊕. It's `NaN` when insolation is unknown.
- **Planet kind:** set by radius; when the radius is missing, by mass; with neither, `exoplanet_unclassified`.

  | Kind | Radius | Mass (fallback) |
  | --- | --- | --- |
  | `planet_terrestrial` | < 1.25 R⊕ | < 2 M⊕ |
  | `planet_super_earth` | < 2.0 R⊕ | < 10 M⊕ |
  | `planet_mini_neptune` | < 6.0 R⊕ | < 50 M⊕ |
  | `planet_gas_giant` | larger | larger |
- **Host [Fe/H]:** the measured `st_met` is used where present (Measured 0.85). Otherwise it's modeled from the gradient (Modeled 0.40).

### Massive-star helpers

| Name | Description |
| --- | --- |
| `estimate_ob_mass(spectral_type)` | Approximate initial mass of an O or B star from its spectral type, interpolated in log mass from three calibration tables (dwarf, giant, supergiant). NaN if the type can't be read. Modeled, good to a factor of ~1.5 |
| `draw_clocks(ids, lifetimes=None, remaining_myr_max=None)` | Statistical collapse times for stars of unknown age: a uniform fraction of each lifetime, or a uniform time up to `remaining_myr_max`. Each draw is seeded by the star's id and `CLOCK_SEED`, so it is reproducible and doesn't change when other stars are added |
| `drop_sky_duplicates(rows, against, radius_arcsec=5)` | The rows with no counterpart in `against` within the radius on the sky |
| `CORE_COLLAPSE_MIN_MASS_MSUN` | 8.0 |
| `WR_PROGENITOR_MASS_MSUN`, `WR_MAX_REMAINING_MYR` | 30.0, 0.5 |
| `DUPLICATE_RADIUS_ARCSEC`, `CLOCK_SEED` | 5.0, 20261022 |

### Provenance helpers

| Name | Description |
| --- | --- |
| `attach_provenance(df, field_map, rows=None)` | Writes `F__tier` and `F__conf` for each field in `field_map` wherever `F` has a value, optionally only on the boolean `rows` |
| `enforce_provenance_default(entities)` | The ADR-011 fail-safe. Any present value with no provenance becomes Speculative / 0.10 (`fields.factor.DEFAULT_FIELD_CONFIDENCE`) |
| `HYG_FIELD_MAP`, `HAZARD_FIELD_MAP`, `EXOPLANET_FIELD_MAP`, `WR_FIELD_MAP`, `OB_FIELD_MAP`, `MODELED_FEH` | Field → `(tier, confidence)`, copied from the source descriptions |
| `MEASURED`, `INFERRED`, `STATISTICAL`, `MODELED`, `SPECULATIVE` | The five tier names |

### Other helpers

| Name | Description |
| --- | --- |
| `modeled_feh(r_gal_kpc)` | EQ-CHEM-1 [Fe/H] at a radius, from the same constants as `MetallicityBandKernel` |
| `luminosity_class(spectral_type)` | The Roman-numeral class, e.g. `"M2Ib"` → `"Ib"`, `"K0"` → `None` |
| `classify_star(spectral_type)` | `white_dwarf` (types starting with D); `star_supergiant` (I, Ia, Iab, Ib); `star_giant` (II, III); otherwise `star_main_sequence` |

---

## The entity table

`load_entities` returns a pandas DataFrame with one row per object. The 77 columns (`ENTITY_COLUMNS`) come in three groups:

1. **5 identity columns (`IDENTITY_COLUMNS`):** `id`, `name`, `kind`, `data_source`, `parent_star_id`. They carry no provenance.
2. **24 physical columns (`PHYSICAL_FIELDS`).**
3. **48 provenance columns:** `F__tier` and `F__conf` for each physical column `F`.

**Ids:**
- HYG stars: `hyg:<HYG id>`. The Sun is `hyg:0`.
- Exoplanet systems: `exo-sys:<host>`.
- Planets: `exo:<planet name>`. A planet's `parent_star_id` is its system's id.

**Kinds produced in Phase 0:** `star_main_sequence`, `star_giant`, `star_supergiant`, `white_dwarf`, `star_massive_progenitor`, `star_wolf_rayet`, `planetary_system`, `planet_terrestrial`, `planet_super_earth`, `planet_mini_neptune`, `planet_gas_giant`, `exoplanet_unclassified`.

| Physical column | Unit | Filled for | Typical provenance |
| --- | --- | --- | --- |
| `ra_icrs_deg`, `dec_icrs_deg` | deg | all | Measured 0.98 |
| `distance_pc` | pc | all | Measured 0.85 (HYG), 0.90 (archive) |
| `x_gal_kpc`, `y_gal_kpc`, `z_gal_kpc` | kpc | all | Same as distance |
| `r_gal_kpc`, `z_height_kpc` | kpc | all | Same as distance |
| `mag_apparent_v`, `mag_absolute_v` | mag | stars | Measured 0.95 / 0.85 |
| `color_bv` | mag | stars | Measured 0.90 |
| `spectral_type` | — | stars | Measured 0.70 |
| `luminosity_lsun` | L☉ | stars, systems | Inferred 0.80 (HYG), Measured 0.80 (archive) |
| `teff_k` | K | stars, systems | Inferred 0.65 (HYG), Measured 0.85 (archive) |
| `mass_msun` | M☉ | main-sequence stars, systems, progenitors | Inferred 0.50 (HYG), Inferred 0.70 (archive), Speculative 0.30 (curated) |
| `feh` | dex | stars, systems | Modeled 0.40, or Measured 0.85 for archive hosts with `st_met` |
| `main_sequence_lifetime_myr` | Myr | progenitors | Speculative 0.30 |
| `t_birth_myr`, `t_collapse_myr` | Myr | progenitors | Speculative 0.10 (scenario values) |
| `num_planets`, `num_planets_in_hz` | — | systems | Measured 0.95 / Inferred 0.70 |
| `planet_radius_rearth` | R⊕ | planets | Measured 0.85 |
| `insolation_earth_equiv` | S⊕ | planets | Inferred 0.75 |
| `in_habitable_zone` | bool | planets | Inferred 0.70 |

The pipeline writes the table to `data/processed/entities.csv` on every run, so you can inspect it directly.

---

## registry (`veil.registry`)

Turns entities and configs into fields.

| Function | Description |
| --- | --- |
| `build_fields(entities, config_dir, project_hazards=False, local_patch=None)` | Returns `(galactic, local)`. `galactic` is loaded from `config_dir/phase0-galactic.toml`. `local` is `LogOddsField.combine([galactic, build_hazard_field(...)])`. With `local_patch = (center, half_width_kpc)`, only hazards that can reach that patch are included; with thousands of catalog hazards, evaluating them all would be far too slow |
| `build_hazard_field(entities, project_onto_plane=False)` | One supernova factor per row whose kind is in `HAZARD_KINDS`, with baseline 0 |
| `hazards_reaching(entities, center, half_width_kpc, project_onto_plane=False)` | The hazards within `SN_REACH_KPC` of a square patch in x and y, and (unless projected) in z. Every other hazard contributes exactly zero there |
| `supernova_factor(entity, project_onto_plane=False)` | The FAC-SN `Factor` for one entity row. See below |
| `evaluate_at_entities(field, entities, t)` | Evaluates a field at each entity's own position. Returns a DataFrame indexed like `entities`, with `habitability_here`, `confidence_here` and `logit_here` (entity.md group 10) |
| `near(entities, center, half_width_kpc)` | The entities whose (x, y) falls inside a square patch |

**`supernova_factor`** combines:
- **Spatial:** `TruncatedInverseSquareKernel(SN_KILL_RADIUS_KPC, SN_CUTOFF_FACTOR)` centered on the star.
- **Time:** a `RampSpikeDecayProfile` built from the star's `t_birth_myr`, `t_collapse_myr` and `SN_DECAY_MYR`.
- **Input confidences:** read from the row's `x_gal_kpc__conf`, `mass_msun__conf` and `t_collapse_myr__conf`.
- **Distance:** true 3D (`EuclideanDistance`) by default. With `project_onto_plane=True` it's `CylindricalDistance`, which measures in the plane only. That shows every star's dip but overstates the reach of stars far off the plane (ADR-014).

| Constant | Value | Source |
| --- | --- | --- |
| `SN_SIGN` | −1 | `factors.md` FAC-SN |
| `SN_MAGNITUDE` | 3.7 | Calibrated, ADR-013 |
| `SN_BACKING` | 0.9 | `factors.md` |
| `SN_KILL_RADIUS_KPC` | 0.010 (10 pc) | `factors.md` Appendix A |
| `SN_DECAY_MYR` | 2.0 | Phase 0 spec §6.8 |
| `SN_CUTOFF_FACTOR`, `SN_REACH_KPC` | 5.0, 0.05 kpc | The kernel's cutoff; no effect beyond it |
| `HAZARD_KINDS` | `star_massive_progenitor`, `star_wolf_rayet` | The kinds that get a FAC-SN factor |

---

## interactive (`veil.interactive`)

Builds the self-contained Plotly page. Surface height is H; surface color is confidence on the canonical blue (1.0) → purple (0.5) → red (0.0) scale. The H axis is fixed at [0, 1] in every frame.

| Function | Description |
| --- | --- |
| `galactic_figure(field, grid, groups)` | The galactic-scale surface at t = 0, with one marker layer per entry in `groups` (`{"system": df, "hazard": df, "sun": df}`) |
| `local_figure(field, grid, animated, static, times, projected=False)` | The local surface with one animation frame per entry in `times`, a slider, and a Play button. `animated` marker groups are recomputed every frame. `static` groups are drawn once at `times[0]`, which keeps the page small when there are thousands of markers |
| `write_html(figures, out_path, projected=False)` | Writes one page containing all `figures`, with plotly.js inlined once. It passes `auto_play=False`; otherwise Plotly starts the animation on load |
| `intro_html(projected=False)` | The page header with honesty notes. The geometry note depends on `projected` |
| `hover_text(entity, here, t)` | One marker's tooltip: each value shown with its `[tier confidence]`, the least-certain field, H and confidence at the entity, and its data source. Massive stars also show time to collapse |
| `lowest_confidence(entity)` | `(field, confidence)` of the entity's least-trusted value, or `None` |

| Constant | Description |
| --- | --- |
| `CONFIDENCE_COLORSCALE` | The red → purple → blue scale |
| `MARKER_STYLES` | Group → (legend name, color, size, symbol) for `sun`, `hazard` and `system` |
| `MARKER_LIFT` | 0.015. Markers sit this far above the surface so they stay visible |
| `SLICE_NOTE`, `PROJECTED_NOTE` | The two wordings of the geometry honesty note |

---

## main (`veil.main`)

| Function | Description |
| --- | --- |
| `main(argv=None)` | The whole pipeline: fetch → ingest → Sun check → build fields → static PNGs → HTML. `argv` follows `argparse` conventions, so tests can call `main([...])` |
| `parse_args(argv=None)` | The command-line options; see [`code-cli-reference.md`](code-cli-reference.md) |
| `check_sun(entities)` | Acceptance spot-check. Raises `RuntimeError` unless the Sun is within 0.1 kpc of R₀ and 0.05 kpc of the plane. Returns its position |

| Constant | Value |
| --- | --- |
| `REPO` | The repository root, found from this file's location |
| `RAW`, `PROCESSED`, `CONFIGS` | `data/raw/`, `data/processed/`, `configs/` |
| `SUN_ID` | `"hyg:0"` |
| `GALACTIC_HTML_SPEC` | ±20 kpc, 200 cells. Coarser than the static grid, to keep the page small |
| `LOCAL_HTML_SPEC` | ±0.25 kpc, 150 cells (~3 pc per cell) |
