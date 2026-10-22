# Data Source: Gaia DR3 Star Clusters (Hunt & Reffert 2023)

> A description of the Hunt & Reffert (2023) census of Milky Way star clusters, following `data-source-info-schema.md`. Doubles as the ingestion crosswalk for `ingest.py` (`load_clusters`). Supplies thousands of open and globular clusters with Gaia-based distances and isochrone ages across several kpc — real points far beyond the solar neighbourhood, and real ages for the time axis.

## Metadata

| Attribute | Value |
| --- | --- |
| `source_id` | `hunt_reffert_2023` |
| `name` | Improving the open cluster census II: an all-sky cluster catalogue with Gaia DR3 (main catalogue, table 3) |
| `provider` | Hunt E.L. & Reffert S., A&A 673, A114 (2023); served by CDS VizieR (`J/A+A/673/A114/clusters`) |
| `url` | <https://vizier.cds.unistra.fr/viz-bin/VizieR?-source=J/A+A/673/A114> |
| `access` | Open; VizieR ASU (HTTP) query, no registration |
| `license_terms` | VizieR/CDS terms: free reuse with citation of the original paper and acknowledgement of VizieR |
| `data_level` | 3 (science-ready catalog) |
| `version` | 2023 publication (Gaia DR3); pin the retrieval date in `data/raw/retrieved.json` |
| `size` | 7,167 clusters; 4,025 pass the quality cut and are kept |
| `coverage` | All-sky; kept clusters have median distance ~1.8 kpc, 90% within ~3.7 kpc. Completeness falls with distance and toward dusty regions |
| `retrieval` | `veil.fetch` — VizieR ASU tab-separated download |

## Provenance classification

| Attribute | Value |
| --- | --- |
| `default_tier` | Measured (positions, distances); Inferred (ages, member counts) |
| `feeds` | **load-bearing** for positions; **provisional** for ages |

## Field map

| field (→ `entity.md`) | source_field | type | unit | provenance_tier | confidence | derivation | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `id` | `Name` | string | — | Measured | 1.00 | — | stored as `cluster:<Name>` |
| `name` | `Name` | string | — | Measured | 1.00 | — | underscores shown as spaces |
| `kind` | `Type` | enum | — | — | — | — | `o` → `open_cluster`, `g` → `globular_cluster`; moving groups (`m`) left out |
| `ra_icrs_deg` | `RA_ICRS` | float | deg | Measured | 0.98 | — | — |
| `dec_icrs_deg` | `DE_ICRS` | float | deg | Measured | 0.98 | — | — |
| `distance_pc` | `dist50` | float | pc | Measured | 0.90 | — | median distance from the members' mean Gaia DR3 parallax — far more precise than any single star |
| `x/y/z/r_gal_kpc` | (derived) | float | kpc | Measured | 0.90 | EQ-GEO-2 | via astropy from ra/dec/distance |
| `age_myr` | `logAge50` | float | Myr | Inferred | 0.60 | 10^logAge / 10⁶ | neural-network isochrone fit; soft for old, sparse, or reddened clusters |
| `num_members` | `N` | int | — | Inferred | 0.80 | — | depends on the membership algorithm and the Gaia magnitude limit |

## Known limitations & systematics

- **Quality cut:** kept clusters have significance `CST` ≥ 5σ and colour–magnitude-diagram class `CMDCl50` ≥ 0.5, which drops many low-significance candidates. I believe these are the thresholds the authors suggest for a reliable sample; check the paper before quoting them as such.
- **Ages:** fitted automatically; uncertainties (`logAge16`–`logAge84`) can span a factor of two or more for faint clusters.
- **Selection:** distant and heavily reddened clusters are under-represented.
- **Not model input (yet):** clusters are drawn for context. Turning young clusters into statistical supernova sources would be a model change, to be proposed first (see `GOVERNANCE.md`).

## Ingestion mapping notes (`load_clusters`)

1. **Query:** ASU columns `Name, Type, CST, N, RA_ICRS, DE_ICRS, dist16, dist50, dist84, logAge16, logAge50, logAge84, CMDCl50, r50pc`, with `-out.max=unlimited`.
2. **Parse:** `read_vizier_tsv` drops `#` comment lines and the units and divider rows under the header, and strips padding from text fields.
3. **Filter:** types `o` and `g`; `CST ≥ 5`; `CMDCl50 ≥ 0.5`; positive `dist50`.
4. **Unit fix:** `logAge50` (log₁₀ years) → Myr.
5. **Provenance:** every value written with the tier and confidence above.
