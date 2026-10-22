# Data Source: ALS III Massive Stars (Pantaleoni González et al. 2021)

> A description of the third Alma Luminous Star catalogue (ALS III), following `data-source-info-schema.md`. Doubles as the ingestion crosswalk for `ingest.py` (`load_ob_stars`). Supplies O and early-B stars — future core-collapse supernovae — as point hazards (`FAC-SN`) across several kpc of the disk.

## Metadata

| Attribute | Value |
| --- | --- |
| `source_id` | `als_iii` |
| `name` | ALS III: Galactic luminous OB stars with Gaia EDR3 distances (table A1) |
| `provider` | Pantaleoni González M., Maíz Apellániz J., Barbá R.H., Reed B.C., MNRAS 504, 2968 (2021); served by CDS VizieR (`J/MNRAS/504/2968/tablea1`) |
| `url` | <https://vizier.cds.unistra.fr/viz-bin/VizieR?-source=J/MNRAS/504/2968> |
| `access` | Open; VizieR TAP query, no registration |
| `license_terms` | VizieR/CDS terms: free reuse with citation of the original paper and acknowledgement of VizieR |
| `data_level` | 3 (science-ready, compiled catalog) |
| `version` | 2021 publication; pin the retrieval date in `data/raw/retrieved.json` |
| `size` | 15,662 stars; ~5,300 kept as supernova progenitors |
| `coverage` | Luminous OB stars across the disk; median distance ~2.1 kpc, 90% within ~4 kpc. About 44% of entries have no spectral type |
| `retrieval` | `veil.fetch` — VizieR TAP synchronous query to CSV |

## Provenance classification

| Attribute | Value |
| --- | --- |
| `default_tier` | Measured (positions, spectral types); Inferred (distances); Modeled (masses) |
| `feeds` | **provisional** (positions are real; masses are estimated and collapse timing is statistical) |

## Field map

| field (→ `entity.md`) | source_field | type | unit | provenance_tier | confidence | derivation | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `id` | `ALS` | string | — | Measured | 1.00 | — | stored as `als:<ALS number>` |
| `name` | `GOSC`, `ALS` | string | — | Measured | 1.00 | — | Galactic O-Star Catalog name where present, e.g. `HD 46223 (ALS 1)` |
| `ra_icrs_deg` | `RAJ2000` | float | deg | Measured | 0.98 | — | — |
| `dec_icrs_deg` | `DEJ2000` | float | deg | Measured | 0.98 | — | — |
| `distance_pc` | `DistP50` | float | pc | Inferred | 0.75 | — | posterior median of a Bayesian distance from a Gaia EDR3 parallax |
| `x/y/z/r_gal_kpc` | (derived) | float | kpc | Inferred | 0.75 | EQ-GEO-2 | via astropy from ra/dec/distance |
| `spectral_type` | `SpType` | string | — | Measured | 0.80 | — | first of several listed classifications |
| `mass_msun` | (derived) | float | M☉ | Modeled | 0.30 | — | `estimate_ob_mass`: approximate calibration by subtype and luminosity class, good to a factor of ~1.5 |
| `main_sequence_lifetime_myr` | (derived) | float | Myr | Modeled | 0.30 | EQ-STAR-1 | from the estimated mass |
| `t_collapse_myr` | (drawn) | float | Myr | Statistical-only | 0.30 | — | a uniform fraction of the lifetime remains, seeded per star — one realization |
| `t_birth_myr` | (derived) | float | Myr | Statistical-only | 0.30 | — | collapse − lifetime |

## Known limitations & systematics

- **Spectral types:** ~6,900 entries have none and can't be given a mass, so they are left out. This under-counts hazards, most in faint, distant regions.
- **Mass calibration:** rounded from standard calibrations from memory (e.g. Martins et al. 2005 for O stars); verify against the literature before using any single star's mass. Supergiants are probably under-estimated (Rigel comes out at ~13 M☉ against ~21).
- **The 8 M☉ cut:** stars near the threshold are uncertain either way; a different calibration would move hundreds of B stars in or out.
- **Timing:** ages are unknown, so collapse times are drawn at random — a statistical scenario, not a prediction.
- **Dust:** like any optical catalog, ALS III misses stars behind heavy extinction.

## Ingestion mapping notes (`load_ob_stars`)

1. **Query:** `ALS, GaiaDR2, GOSC, RAJ2000, DEJ2000, DistP50, DistP16, DistP84, SpType`.
2. **Filter:** drop rows with no positive `DistP50`; estimate mass from `SpType`; keep stars with mass ≥ 8 M☉. Wolf-Rayet entries (types starting `W`) give no O/B mass and drop out; they come from `source-galactic-wr-catalogue.md` instead.
3. **Kind:** `star_massive_progenitor`.
4. **Clock:** `draw_clocks` with `lifetimes`; reject any star that would be born in the future.
5. **Duplicates:** rows within 5″ of a curated or Wolf-Rayet hazard are dropped; HYG rows within 5″ of an ALS III star are dropped.
6. **Provenance:** every value written with the tier and confidence above.
