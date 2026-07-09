# Equations — Load-Bearing Set (Fundamental & Established)

> **The trustworthy tier.** This document contains *only* equations rated **Fundamental** or **Established** — physical laws and well-supported empirical relations. By living in this file, an equation is structurally classified as load-bearing: the pipeline may treat results derived solely from this set as high-confidence. Anything Approximate, Construct, Partial, or Missing lives in `equations-provisional.md` and must never be silently mixed in as if it belonged here. This structural split (source document = classification) is ADR-011. Shared conventions and the certainty legend live in `schema-field-definition.md` and the header of `equations-provisional.md`.

Certainty ratings: **Fundamental** (exact within regime) · **Established** (empirical, well-supported, known scatter).

## Core field model

| ID | Name | Form | Purpose | Certainty |
| --- | --- | --- | --- | --- |
| `EQ-CORE-1` | Log-odds combination | `logit(H) = B₀ + Σᵢ ℓᵢ` | Combine factor contributions in log-odds | Fundamental |
| `EQ-CORE-2` | Logistic transform | `H = 1/(1+e^(−logit))` | Map log-odds to probability (veil height) | Fundamental |

## Geometry & coordinates

| ID | Name | Form | Purpose | Certainty |
| --- | --- | --- | --- | --- |
| `EQ-GEO-1` | Distance from parallax | `d(pc) = 1000/ϖ(mas)` | Distance from Gaia parallax | Fundamental |
| `EQ-GEO-2` | ICRS → galactocentric | rotation+translation (astropy) | Place entities in galaxy frame | Fundamental |
| `EQ-GEO-3` | Cylindrical radius | `R = √(x²+y²)` | Galactocentric radius | Fundamental |

## Stellar physics

| ID | Name | Form | Purpose | Certainty |
| --- | --- | --- | --- | --- |
| `EQ-STAR-2` | Stefan–Boltzmann | `L = 4πR²σT⁴` | Luminosity/radius/temperature | Fundamental |
| `EQ-STAR-3` | Wien's displacement | `λ_peak = b/T` | Spectral peak from temperature | Fundamental |
| `EQ-STAR-4` | Photon energy / red limit | `E = hc/λ`; oxygenic ≈1.8 eV | Photosynthetic photon limit | Fundamental |

## Habitable zone & planets

| ID | Name | Form | Purpose | Certainty |
| --- | --- | --- | --- | --- |
| `EQ-HZ-1` | Insolation | `S/S⊕ = (L/L☉)/(a/AU)²` | Stellar flux at a planet | Fundamental |
| `EQ-HZ-2` | HZ boundaries | `a = √[(L/L☉)/S]`, `S_in≈1.1, S_out≈0.35` | Habitable-zone edges | Established |
| `EQ-HZ-3` | Equilibrium temperature | `T_eq = T★·√(R★/2a)·(1−A)^¼` | Planet climate regime | Fundamental |
| `EQ-HZ-4` | Kepler III | `P² = a³/(M/M☉)` | Orbital period from orbit | Fundamental |

## Chemical evolution (established relations)

| ID | Name | Form | Purpose | Certainty |
| --- | --- | --- | --- | --- |
| `EQ-CHEM-1` | Radial metallicity gradient | `[Fe/H](R) ≈ [Fe/H]₀ − 0.06·(R−R₀)` | Modeled metallicity vs radius | Established |
| `EQ-CHEM-2` | Giant-planet occurrence | `P(giant) ≈ 10^(2·[Fe/H])` | Planet–metallicity correlation | Established |

## Spatial structure

| ID          | Name                 | Form                                       | Purpose                   | Certainty   |
|-------------|----------------------|--------------------------------------------|---------------------------|-------------|
| `EQ-PROF-1` | Disk density profile | `n(R,z)=n₀·e^(−(R−R₀)/h_R)·e^(−\|z\|/h_z)` | Statistical density field | Established |

---

*Constants for these equations (with uncertainties and sources) are in `factors.md` Appendix A. Any equation not listed here is provisional by definition — see `equations-provisional.md`.*
