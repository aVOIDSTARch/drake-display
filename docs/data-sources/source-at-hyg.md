# Data Source: AT-HYG Database

> A description of the AT-HYG star catalog, following `data-source-info-schema.md`. Doubles as the ingestion crosswalk for `ingest.py`. Provides the stellar backbone for Phase 0.

## Metadata

| Attribute | Value |
| --- | --- |
| `source_id` | `at_hyg` |
| `name` | AT-HYG (Augmented Tycho + HYG) Database |
| `provider` | Astronexus (David Nash) |
| `url` | <https://github.com/astronexus/HYG-Database> |
| `access` | Open; plain CSV on GitHub, no registration |
| `license_terms` | CC BY-SA 4.0 (per repository) — attribute and share-alike; governs reuse, not this project's licenses |
| `data_level` | 3 (science-ready, compiled catalog) |
| `version` | AT-HYG v3 (Gaia-augmented); classic HYG v3 also usable |
| `size` | ~2.5 million stars (AT-HYG); ~120,000 (classic HYG) |
| `coverage` | All-sky; precise for nearby stars, degrading with distance; magnitude-limited |
| `retrieval` | CSV download from GitHub |

## Provenance classification

| Attribute | Value |
| --- | --- |
| `default_tier` | Measured / Direct (astrometry); derived stellar parameters overridden per-field below |
| `feeds` | **load-bearing** (positions & distances are the trustworthy backbone); derived params feed provisional |

## Field map

| field (→ `entity.md`) | source_field | type | unit | provenance_tier | confidence | derivation | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `id` | `id` (+ `hip`/`hd`/`gaia`) | string | — | Measured | 1.00 | — | stable catalog IDs; retain all cross-IDs |
| `name` | `proper` | string | — | Measured | 1.00 | — | present only for named stars |
| `ra_icrs_deg` | `ra` | float | deg | Measured | 0.98 | ×15 (hours→deg) | **`ra` is in HOURS in HYG — convert** |
| `dec_icrs_deg` | `dec` | float | deg | Measured | 0.98 | — | already in degrees |
| `distance_pc` | `dist` | float | pc | Measured | 0.85 | — | Gaia/Hipparcos parallax; degrades for faint/distant; **`dist=100000` = unknown, drop** |
| `x_gal_kpc` | (derived) | float | kpc | Measured | 0.85 | EQ-GEO-2 | via astropy from ra/dec/dist — **NOT HYG's `x`** (heliocentric equatorial; do not use) |
| `y_gal_kpc` | (derived) | float | kpc | Measured | 0.85 | EQ-GEO-2 | as above |
| `z_gal_kpc` | (derived) | float | kpc | Measured | 0.85 | EQ-GEO-2 | as above |
| `r_gal_kpc` | (derived) | float | kpc | Measured | 0.85 | EQ-GEO-3 | √(x²+y²) |
| `mag_apparent_v` | `mag` | float | mag | Measured | 0.95 | — | apparent visual magnitude |
| `mag_absolute_v` | `absmag` | float | mag | Measured | 0.85 | — | inherits distance uncertainty |
| `color_bv` | `ci` | float | mag | Measured | 0.90 | — | B−V color index |
| `spectral_type` | `spect` | string | — | Measured | 0.70 | — | often coarse or missing |
| `pm_ra_mas_yr` | `pmra` | float | mas/yr | Measured | 0.90 | — | Gaia where available |
| `pm_dec_mas_yr` | `pmdec` | float | mas/yr | Measured | 0.90 | — | — |
| `radial_velocity_km_s` | `rv` | float | km/s | Measured | 0.70 | — | sparse; 0 often means "unmeasured" — treat missing |
| `luminosity_lsun` | (derived) | float | L☉ | Inferred | 0.80 | from `absmag` | bolometric correction approximate |
| `teff_k` | (derived) | float | K | Inferred | 0.65 | from `ci`/`spect` | color–temperature calibration |
| `mass_msun` | (derived) | float | M☉ | Inferred | 0.50 | mass–luminosity relation | **main-sequence only; rough**; drives hazard clock |
| `feh` | (not provided) | float | dex | Modeled | 0.40 | EQ-CHEM-1 | AT-HYG has no metallicity → modeled from radial gradient |

## Known limitations & systematics

- No metallicity, no direct mass — both are absent and must be modeled/estimated (low confidence).
- Distance quality is heterogeneous (mixes Gaia, Hipparcos, older sources); faint/distant stars have poor parallax.
- Magnitude-limited: not a volume-complete sample beyond the solar neighborhood.
- Spectral types are inconsistent in completeness and precision.

## Ingestion mapping notes (`ingest.py`)

1. **Filter:** drop rows with `dist` missing or `dist == 100000` (unknown-distance sentinel); drop non-positive parallax-derived distances.
2. **Unit fix:** convert `ra` (hours) → degrees (×15) before the astropy transform.
3. **Coordinates:** build galactocentric x/y/z from ra/dec/dist via astropy (`EQ-GEO-2`); **ignore HYG's native `x`/`y`/`z`** (wrong frame — ADR-003).
4. **Estimate:** derive `mass_msun` (mass–luminosity, main sequence), `teff_k`, `luminosity_lsun` from magnitude/color/spectral type; flag each Inferred with the confidences above.
5. **Model:** fill `feh` from `EQ-CHEM-1` at the star's `r_gal_kpc`; mark Modeled, 0.40.
6. **Kind assignment:** classify `kind` (`star_main_sequence`, `star_giant`, `star_supergiant`, `star_massive_progenitor`, `brown_dwarf`) from `absmag` + `spect`.
7. **Provenance:** write every value as a cell with `source='at_hyg'`, its tier, and its confidence (per `data-store-schema.md`).
