# Data Source: NASA Exoplanet Archive

> A description of the NASA Exoplanet Archive (Planetary Systems table), following `data-source-info-schema.md`. Doubles as the ingestion crosswalk for `ingest.py`. Provides planets, host-star parameters, and — valuably — **measured spectroscopic metallicity**.

## Metadata

| Attribute | Value |
|---|---|
| `source_id` | `nasa_exoarchive` |
| `name` | NASA Exoplanet Archive — Planetary Systems (PS) table |
| `provider` | NASA / IPAC / Caltech |
| `url` | <https://exoplanetarchive.ipac.caltech.edu> |
| `access` | Open; web tables, TAP service, API, bulk CSV |
| `license_terms` | Public domain (U.S. Government / NASA); free reuse with acknowledgement |
| `data_level` | 3 (science-ready) |
| `version` | Continuously updated; pin the retrieval date |
| `size` | ~5,900+ confirmed planets (+ thousands of candidates) |
| `coverage` | Confirmed planetary systems only — a biased, non-volume-complete sample (detection-method selection effects) |
| `retrieval` | TAP/API query or CSV; use `default_flag=1` to get one row per planet |

## Provenance classification

| Attribute | Value |
|---|---|
| `default_tier` | Measured / Direct (confirmed-planet parameters); some derived fields overridden below |
| `feeds` | **load-bearing** (confirmed data; notably a *measured* metallicity source superior to the modeled gradient) |

## Field map

**Host star** (creates/updates a host `star_*` and a `planetary_system` entity):

| field (→ `entity.md`) | source_field | type | unit | provenance_tier | confidence | derivation | notes |
|---|---|---|---|---|---|---|---|
| `name` | `hostname` | string | — | Measured | 1.00 | — | host identifier; used for entity resolution |
| `ra_icrs_deg` | `ra` | float | deg | Measured | 0.98 | — | already in degrees |
| `dec_icrs_deg` | `dec` | float | deg | Measured | 0.98 | — | — |
| `distance_pc` | `sy_dist` | float | pc | Measured | 0.90 | — | mostly Gaia-based |
| `teff_k` | `st_teff` | float | K | Measured | 0.85 | — | spectroscopic |
| `radius_rsun` | `st_rad` | float | R☉ | Measured | 0.80 | — | — |
| `mass_msun` | `st_mass` | float | M☉ | Inferred | 0.70 | — | better than AT-HYG estimate |
| `feh` | `st_met` | float | dex | Measured | 0.85 | — | **spectroscopic metallicity — surfaces over modeled `feh` in conflict resolution** |
| `luminosity_lsun` | `st_lum` | float | L☉ | Measured | 0.80 | — | often log₁₀(L☉); convert |
| `num_planets` | `sy_pnum` | int | — | Measured | 0.95 | — | planets in system |

**Planet** (creates a `planet_*` entity, linked to the host):

| field (→ `entity.md`) | source_field | type | unit | provenance_tier | confidence | derivation | notes |
|---|---|---|---|---|---|---|---|
| `id` | `pl_name` | string | — | Measured | 1.00 | — | unique planet name |
| `parent_star_id` | `hostname` | string | — | Measured | 1.00 | — | foreign key to host |
| `planet_radius_rearth` | `pl_rade` | float | R⊕ | Measured | 0.85 | — | transit radius (if available) |
| `planet_mass_mearth` | `pl_bmasse` | float | M⊕ | Inferred | 0.70 | — | often minimum mass (RV) |
| `semi_major_axis_au` | `pl_orbsmax` | float | AU | Measured | 0.85 | — | — |
| `orbital_period_days` | `pl_orbper` | float | days | Measured | 0.95 | — | very precise for transiting |
| `eq_temp_k` | `pl_eqt` | float | K | Inferred | 0.60 | EQ-HZ-3 | albedo assumed; often derived |
| `insolation_earth_equiv` | `pl_insol` | float | S⊕ | Inferred | 0.75 | EQ-HZ-1 | — |
| `in_habitable_zone` | (derived) | bool | — | Inferred | 0.70 | EQ-HZ-2 | orbit vs. computed HZ |
| `planet_type` | (derived) | enum | — | Inferred | 0.75 | — | from radius/mass thresholds |

## Known limitations & systematics

- **Detection bias:** confirmed planets skew toward large, close-in worlds around bright, nearby stars; not representative of the true population.
- Many masses are **minimum masses** (RV `m·sin i`) — treat `planet_mass_mearth` as a lower bound.
- Equilibrium temperature depends on an assumed albedo; treat as indicative.
- Continuously updated — pin the retrieval date for reproducibility.

## Ingestion mapping notes (`ingest.py`)

1. **Query:** pull the PS table with `default_flag=1` (one canonical row per planet); drop rows lacking `ra`/`dec`/`sy_dist`.
2. **Entity split:** each row yields up to three entities — the **host star**, the **planetary_system**, and the **planet** — linked by `hostname`/`parent_star_id`.
3. **Entity resolution (ADR-012):** match `hostname` against existing `at_hyg` stars (by coordinates/cross-ID). On a match, **merge**; on the `feh` conflict, `st_met` (0.85, Measured) surfaces over the modeled AT-HYG value (0.40, Modeled) — a worked example of the conflict rule.
4. **Unit fixes:** convert `st_lum` from log₁₀(L☉) if logged; confirm units per the archive column definitions.
5. **Derive:** compute `in_habitable_zone` (`EQ-HZ-2`), `planet_type`, and confirm `eq_temp_k`/`insolation` where absent (`EQ-HZ-1/3`).
6. **Provenance:** write every value as a cell with `source='nasa_exoarchive'`, its tier, and its confidence (per `data-store-schema.md`).
