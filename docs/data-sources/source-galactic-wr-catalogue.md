# Data Source: Galactic Wolf-Rayet Catalogue (Rate & Crowther 2020)

> A description of the Gaia-based Galactic Wolf-Rayet catalogue, following `data-source-info-schema.md`. Doubles as the ingestion crosswalk for `ingest.py` (`load_wolf_rayet`). Supplies Wolf-Rayet stars — massive stars in their last few hundred thousand years before core collapse — as point hazards (`FAC-SN`) across several kpc of the disk.

## Metadata

| Attribute | Value |
| --- | --- |
| `source_id` | `galactic_wr_rate_crowther_2020` |
| `name` | Gaia DR2 properties of Galactic Wolf-Rayet stars (table 1) |
| `provider` | Rate G. & Crowther P.A., MNRAS 493, 1512 (2020); served by CDS VizieR (`J/MNRAS/493/1512/table1`) |
| `url` | <https://vizier.cds.unistra.fr/viz-bin/VizieR?-source=J/MNRAS/493/1512> |
| `access` | Open; VizieR TAP query, no registration |
| `license_terms` | VizieR/CDS terms: free reuse with citation of the original paper and acknowledgement of VizieR |
| `data_level` | 3 (science-ready, compiled catalog) |
| `version` | 2020 publication; pin the retrieval date in `data/raw/retrieved.json` |
| `size` | 383 stars listed; 380 returned with a distance |
| `coverage` | Galactic WR stars with Gaia DR2 parallaxes; median distance ~2.9 kpc, 90% within ~5.9 kpc. Incomplete: dust hides many WR stars in the inner disk |
| `retrieval` | `veil.fetch` — VizieR TAP synchronous query to CSV |

## Provenance classification

| Attribute | Value |
| --- | --- |
| `default_tier` | Measured (positions, spectral types); Inferred (distances); overridden per field below |
| `feeds` | **provisional** (hazard positions are real; masses and collapse timing are not measured) |

## Field map

| field (→ `entity.md`) | source_field | type | unit | provenance_tier | confidence | derivation | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `id` | `WR` | string | — | Measured | 1.00 | — | stored as `wr:<WR number>` |
| `name` | `WR` + `Name` | string | — | Measured | 1.00 | — | e.g. `WR11 (gam2 Vel)` |
| `ra_icrs_deg` | `RA_ICRS` | float | deg | Measured | 0.98 | — | — |
| `dec_icrs_deg` | `DE_ICRS` | float | deg | Measured | 0.98 | — | — |
| `distance_pc` | `Dist` | float | pc | Inferred | 0.70 | — | catalog gives **kpc**; ×1000. Bayesian distance from a Gaia DR2 parallax |
| `x/y/z/r_gal_kpc` | (derived) | float | kpc | Inferred | 0.70 | EQ-GEO-2 | via astropy from ra/dec/distance |
| `spectral_type` | `SpType` | string | — | Measured | 0.85 | — | WN/WC/WO subtype, sometimes with a companion |
| `luminosity_lsun` | `logL` | float | L☉ | Inferred | 0.60 | 10^logL | missing for some stars |
| `mass_msun` | (assigned) | float | M☉ | Speculative | 0.20 | — | a typical progenitor initial mass, 30 M☉, **not this star's**; used only to set the ramp length |
| `main_sequence_lifetime_myr` | (derived) | float | Myr | Speculative | 0.20 | EQ-STAR-1 | from the assigned mass |
| `t_collapse_myr` | (drawn) | float | Myr | Statistical-only | 0.30 | — | uniform in [0, 0.5] Myr from now, seeded per star — one realization |
| `t_birth_myr` | (derived) | float | Myr | Statistical-only | 0.30 | — | collapse − lifetime |

## Known limitations & systematics

- **Selection:** WR stars behind heavy dust (much of the inner disk) are missing, so the hazard map under-counts toward the galactic center.
- **Distances:** Gaia DR2 parallaxes for distant, reddened WR stars are uncertain; several-kpc distances carry tens of percent error.
- **Timing:** no WR star's collapse date is known. The WR phase lasts a few hundred thousand years, so a collapse within 0.5 Myr is drawn at random — a statistical scenario, not a prediction.
- **Binaries:** many WR stars have O-type companions, which are also future supernovae but are not added separately.

## Ingestion mapping notes (`load_wolf_rayet`)

1. **Query:** `WR, SpType, Name, RA_ICRS, DE_ICRS, Dist, "E_Dist", "e_Dist", logL`. The two error columns must be quoted: ADQL names are case-insensitive, and they differ only by case.
2. **Filter:** drop rows with no positive `Dist`.
3. **Unit fix:** `Dist` kpc → pc.
4. **Kind:** `star_wolf_rayet`, which `veil.registry` treats as a supernova hazard.
5. **Clock:** `draw_clocks` with `remaining_myr_max = 0.5`; reject any star that would be born in the future.
6. **Duplicates:** rows within 5″ of a curated hazard are dropped (curated wins); HYG rows within 5″ of a WR star are dropped.
7. **Provenance:** every value written with the tier and confidence above.
