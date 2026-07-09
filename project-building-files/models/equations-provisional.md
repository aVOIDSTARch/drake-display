# Equations — Provisional Set (Approximate / Construct / Partial / Missing)

> **The lower-confidence tier.** Everything here is *not* a settled physical law: order-of-magnitude fits (**Approximate**), modeling choices (**Construct**), assembled-from-pieces (**Partial**), or not-yet-existing (**Missing**). By living in *this* document rather than `equations-core.md`, an equation is structurally classified as provisional — the pipeline must propagate reduced confidence to any result that depends on it, and the render must shade it toward red/purple. This split is ADR-011. The confidence scale and color mapping are defined once in `schema-field-definition.md`.

Certainty ratings: **Approximate** · **Construct** (a defined modeling choice, tunable, not "true") · **Partial** (pieces exist; not fully assembled) · **Missing** (no equation yet).

## Core model constructs
| ID | Name | Form | Purpose | Certainty |
|---|---|---|---|---|
| `EQ-CORE-3` | Factor contribution | `ℓᵢ = signᵢ·wᵢ·Mᵢ·fᵢ(space)·gᵢ(t)` | Per-factor log-odds term | Construct |
| `EQ-CORE-4` | Confidence propagation | *(now defined — see below)* | Aggregate trustworthiness of a veil value → the blue/purple/red hue | Construct |

### `EQ-CORE-4` — Confidence propagation (newly defined)
Previously **Missing**; now specified as a defensible **Construct**. It answers: *how much should we trust the veil's height at this point and time?* — and its output drives the color.

**Step 1 — per-factor input confidence (weakest link).** A factor reads one or more entity fields, each with its own `confidence` (from `schema-field-definition.md` / the source field map). The factor's input confidence is the **minimum** over those fields (a factor is only as trustworthy as its least-certain input):
`c_input,i = min( confidence of each entity field factor i reads )`
*(Default per field, if absent: 0.10. Alternative to `min`: the product, for stricter multiplicative degradation — `min` is the conservative default.)*

**Step 2 — combined per-factor confidence.** Fold in the factor's own science-backing weight `wᵢ` (from `factors.md`):
`cᵢ = wᵢ · c_input,i`

**Step 3 — location confidence (magnitude-weighted mean).** Trust the veil value in proportion to how much of its log-odds comes from high-confidence factors:
`confidence_here = Σᵢ cᵢ·|ℓᵢ|  /  Σᵢ |ℓᵢ|`
*(If `Σ|ℓᵢ| = 0`, confidence is undefined → treat as low/baseline.)*

**Step 4 — render.** Map `confidence_here` onto the canonical blue(1.0)→purple(0.5)→red(0.0) hue scale (`schema-field-definition.md` §5). Height still comes from `H`; hue comes from `confidence_here`. Thus a **red result formed where a blue-certain input and a red-uncertain input combine** is exactly uncertainty propagating through the log-odds sum — the picture the user envisioned, now with math beneath it.

**Status:** Construct — the *method* is a defensible modeling choice, not a law; tunable (min vs product, weighting). It is defined and usable, no longer Missing.

## Stellar physics
| ID | Name | Form | Purpose | Certainty |
|---|---|---|---|---|
| `EQ-STAR-1` | Main-sequence lifetime | `t_MS ≈ 10¹⁰·(M/M☉)^(−2.5) yr` | Hazard clock (collapse timing) | Approximate |

## Chemical evolution (gaps)
| ID | Name | Form | Purpose | Certainty |
|---|---|---|---|---|
| `EQ-CHEM-3` | Metallicity→habitability band | `—` (optimum band) | Metallicity as habitability factor | Partial |
| `EQ-CHEM-4` | Metallicity vs cosmic time | `[Fe/H](R,t) = ?` | Time-evolving metallicity ridge | Missing |
| `EQ-CHEM-5` | Radiogenic heat→tectonics | `—` from Th/U/K | Tectonic/dynamo habitability | Missing |

## Hazard physics
| ID | Name | Form | Purpose | Certainty |
|---|---|---|---|---|
| `EQ-HAZ-1` | SN lethality vs distance | ozone ∝ 1/d²; `r_k≈8–10 pc` | Supernova dip reach | Partial |
| `EQ-HAZ-2` | GRB lethal fluence | `Φ≈100 J/m²`; ~1–2 kpc | GRB dip reach | Approximate |
| `EQ-HAZ-3` | GRB rate per volume/time | `R_GRB ∝ SFR·f([Fe/H])` | Statistical GRB field | Partial |
| `EQ-HAZ-4` | Survival probability | `S = exp(−λτ)` | Hazard-aware Drake multiplier | Approximate (framework) |
| `EQ-HAZ-5` | Beaming duty factor | `f_beam = Ω_jet/4π` | Down-weight beamed GRBs | Approximate |

## Profiles (modeling constructs)
| ID | Name | Form | Purpose | Certainty |
|---|---|---|---|---|
| `EQ-PROF-2` | Point-hazard falloff | `f(d)=min(1, r_k²/(d²+ε))` | Local hazard spatial profile | Construct |
| `EQ-PROF-3` | Hazard temporal ramp | `g(t)=clip((t−t_b)/(t_c−t_b),0,1)³` | Dip deepening to collapse | Construct |
| `EQ-PROF-4` | Post-collapse decay | `g(t)=exp(−(t−t_c)/τ)` | Spike then fade | Construct |

## Energy-for-life
| ID | Name | Form | Purpose | Certainty |
|---|---|---|---|---|
| `EQ-ENERGY-1` | Photosynthetic availability | `—` from stellar SED | Energy positive factor | Partial |
| `EQ-ENERGY-2` | Stellar-longevity bonus | function of `t_MS` | Reward long-lived stars | Construct |

---

## Remaining gaps (still Missing/Partial)
- `EQ-CHEM-3` (Partial), `EQ-CHEM-4` (Missing), `EQ-CHEM-5` (Missing), `EQ-HAZ-1` (Partial), `EQ-HAZ-3` (Partial), `EQ-ENERGY-1` (Partial). *(`EQ-CORE-4` is now resolved — moved from Missing to Construct/defined.)*

*Any equation here degrades the confidence of results that use it; that degradation is carried by the per-field/per-factor confidences and surfaced through `EQ-CORE-4` as red/purple shading.*
