# Schema: Field Definition — The Drake Display

> **The atomic meta-schema.** This document defines the canonical way to describe *any single data field* anywhere in the project, and — critically — it is the **single source of truth for the confidence scale and provenance tiers** that every other document references. If you are describing a field (in `entity.md`, in a data-source description, in a factor input), you describe it with the structure defined here. Governed by `SCHEMAS.md`.

---

## 1. Why this exists

Uncertainty in this project is **per-field, not per-record**: a star's *position* may be rock-solid while its *age* is soft and its *metallicity* is entirely modeled — all in the same row. Therefore trustworthiness must be a mandatory property of *each field value*, with a fail-safe default. This schema makes "forgetting to flag uncertainty" structurally impossible: a field value cannot be fully specified without its confidence.

## 2. The field descriptor (required structure)

Every field is described by these attributes:

| Attribute | Required | Meaning |
| --- | --- | --- |
| `field` | ✓ | Canonical field name (snake_case, matches `entity.md`) |
| `type` | ✓ | Data type: `float`, `int`, `string`, `bool`, `enum`, `datetime`, `array`, `dict` |
| `unit` | ✓ (if physical) | Explicit unit (`kpc`, `pc`, `M☉`, `K`, `Myr`, `AU`, `dex`, …) or `—` |
| `required` | ✓ | Whether the field is mandatory for its entity kind |
| `provenance_tier` | ✓ | One of the five tiers in §3 — determines the default confidence band |
| `confidence` | ✓ | A value in [0,1]; the estimated trustworthiness of *this value from this source* (see §4) |
| `source_field` | — | The originating column/key in the source dataset (for ingestion mapping) |
| `derivation` | — | If computed, the equation ID (`equations-*.md`) that produces it |
| `notes` | — | Caveats, systematics, assumptions |

A value is only "complete" when `provenance_tier` and `confidence` are both present.

## 3. Provenance tiers (canonical — reference these everywhere)

The five tiers, with their **default confidence bands**. These mirror the derivation-map tiers in `factors.md` Appendix B and are the authoritative definition:

| Tier | Meaning | Default confidence band |
| --- | --- | --- |
| **Measured / Direct** | Observed, or computed from observables by exact law | **0.90 – 1.00** |
| **Inferred** | Model-dependent estimate with real scatter (e.g. isochrone mass/age) | **0.50 – 0.85** |
| **Statistical-only** | A distribution, never a deterministic value (e.g. collapse timing, hazard rate) | **0.30 – 0.60** |
| **Modeled** | Filled from a model/gradient, not measured for this object | **0.30 – 0.60** |
| **Speculative** | Placeholder, invented, or running on a Missing/Partial equation | **0.00 – 0.30** |

## 4. The confidence scale (canonical — the one definition)

- **`confidence` ∈ [0,1]** — 1.0 = as trustworthy as anything in the project (a fundamental measurement); 0.0 = pure speculation.
- **Fail-safe default:** if `confidence` is absent or unknown, it is treated as **0.10 (Speculative)** — *never* as certain. Uncertainty is the default; certainty must be earned and stated. This is the structural enforcement of "uncertain until proven."
- Confidence is a property of *a value from a specific source*: the same field (e.g. `feh`) may be 0.95 from a spectroscopic survey and 0.40 when filled from the radial gradient. The source's field map (`data-source-info-schema.md`) supplies the per-source value.

## 5. Canonical color mapping (used by every display)

The visual language for trustworthiness, defined once:

| confidence | hue | reading |
| --- | --- | --- |
| → 1.0 | **blue** | trustworthy / confidently true |
| ≈ 0.5 | **purple** | mixed or moderate evidence |
| → 0.0 | **red** | low confidence / speculative |

Renderers map `confidence` (for fields and equations) and `confidence_here` (for aggregated veil values, via `EQ-CORE-4`) onto this blue→purple→red scale. **Height/probability and hue are independent channels:** a tall *blue* ridge is "confidently habitable"; a tall *red* ridge is "the model says habitable, but don't trust it"; purple is genuinely mixed evidence.

## 6. Worked example

``` text
field: luminosity_lsun
type: float
unit: L☉
required: false
provenance_tier: Measured / Direct
confidence: 0.98
source_field: (derived)
derivation: EQ-STAR-2
notes: from apparent mag + parallax + extinction; extinction error dominates
```

``` text
field: feh            # same field, different source → different confidence
type: float
unit: dex
required: false
provenance_tier: Modeled           # filled from the radial gradient
confidence: 0.40
derivation: EQ-CHEM-1
notes: no spectroscopic measurement for this star; modeled from R
```

## 7. Relationship to `entity.md`

`entity.md` lists *which* fields each entity kind carries; **this schema governs *how* each of those fields is described.** The former `is_speculative` boolean in `entity.md` is superseded by this graded, per-field `confidence` + `provenance_tier` pair (a boolean cannot express "position certain, age soft, metallicity modeled" within one record). `entity.md`'s field tables are henceforth read through this schema.
