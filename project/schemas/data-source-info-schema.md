# Schema: Data-Source Description — The Drake Display

> **The canonical template for describing any data source.** Every catalog, survey, or dataset the project ingests gets one description document that follows this structure. Its centerpiece is a **field map** giving the per-field confidence *for that specific source* — so the pipeline learns not just *what* a source provides but *how much to trust each field it provides*. Built on `schema-field-definition.md` (which defines the confidence scale and provenance tiers) and governed by `SCHEMAS.md`. Use it to turn each entry in `data-sources-catalog.md` into a machine-usable, confidence-aware source spec.

---

## 1. Purpose

A source's trustworthiness varies by field. Gaia's *parallax* is superb; a *photometric metallicity* from the same release is far softer. The naming of the source alone doesn't tell the pipeline this — so each source must declare, field by field, its provenance tier and confidence. This document standardizes that declaration.

## 2. Required structure

Each data-source description contains the following sections.

### 2.1 Source metadata

| Attribute | Required | Meaning |
|---|---|---|
| `source_id` | ✓ | Short stable identifier (e.g. `gaia_dr3`, `nasa_exoarchive`, `at_hyg`) |
| `name` | ✓ | Full name |
| `provider` | ✓ | Organization/mission |
| `url` | ✓ | Access URL |
| `access` | ✓ | How to obtain (open / registration / API / query language) |
| `license_terms` | ✓ | The source's own license/terms (governs reuse — not this project's licenses) |
| `data_level` | ✓ | 0/1/2/3 (raw → calibrated → epoch → science-ready); see `data-sources-catalog.md` |
| `version` | ✓ | Release/version (e.g. DR3) and date |
| `size` | — | Row count / volume |
| `coverage` | ✓ | Spatial, temporal, and completeness limits (e.g. "precise <2 kpc, degrading beyond") |
| `retrieval` | — | Programmatic method (e.g. `astroquery.gaia`, CSV download) |

### 2.2 Provenance classification (the tier gate)

| Attribute | Required | Meaning |
|---|---|---|
| `default_tier` | ✓ | The provenance tier (per `schema-field-definition.md` §3) applied to fields from this source unless overridden per-field |
| `feeds` | ✓ | Which certainty collection this source primarily feeds: `load-bearing` or `provisional` (mirrors the equations split; see ADR-011) |

### 2.3 Field map (the centerpiece)

A table, one row per field this source supplies, each described per `schema-field-definition.md`. The **confidence** column is the per-source estimate — this is the `field: luminosity → confidence: 0.98` mechanism.

| `field` (→ `entity.md`) | `source_field` | `type` | `unit` | `provenance_tier` | `confidence` | `derivation` | `notes` |
|---|---|---|---|---|---|---|---|
| … | … | … | … | … | 0.00–1.00 | eq ID / — | … |

### 2.4 Known limitations & systematics
Free text: selection effects, biases, incompleteness, dust, saturation, distance-degradation — anything that qualifies the confidences above.

### 2.5 Ingestion mapping notes
How `source_field` names map to `entity.md` fields (the crosswalk `ingest.py` needs), plus any unit conversions or filters.

---

## 3. Worked example (abbreviated) — `gaia_dr3`

**Metadata:** `source_id: gaia_dr3` · provider ESA · `data_level: 3` · `version: DR3 (2022)` · coverage "precise 3D within a few kpc, degrading outward." **Provenance:** `default_tier: Measured / Direct` · `feeds: load-bearing`.

**Field map (excerpt):**

| field | source_field | type | unit | tier | confidence | derivation | notes |
|---|---|---|---|---|---|---|---|
| `parallax_mas` | `parallax` | float | mas | Measured | 0.98 | — | zero-point offset applied |
| `distance_pc` | (derived) | float | pc | Measured | 0.95 | EQ-GEO-1 | degrades for small parallax |
| `teff_k` | `teff_gspphot` | float | K | Inferred | 0.80 | — | photometric temperature |
| `feh` | `mh_gspphot` | float | dex | Inferred | 0.55 | — | photometric metallicity; soft |
| `mass_msun` | (derived) | float | M☉ | Inferred | 0.60 | mass–lum | main-sequence only |

**Limitations:** photometric astrophysical parameters are far less reliable than the astrometry; extinction degrades temperature/metallicity in the plane.

---

## 4. The rule this enforces

Because every field from every source carries an explicit `provenance_tier` and `confidence` — and because absence defaults to Speculative (0.10) per `schema-field-definition.md` — **no value can enter the pipeline masquerading as more certain than it is.** The source description is where trustworthiness is declared once and inherited everywhere downstream, all the way to the blue/purple/red shading on screen.
