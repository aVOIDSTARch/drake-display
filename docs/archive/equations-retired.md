# Equations — Reference Set for the Galactic Habitability Veil

> The collection of equations the model needs, in the same structured form as `entity.md`. Each carries its **form**, **purpose/use**, a **certainty** rating, and notes. Where we do **not yet have** a usable equation, it is listed explicitly with status **Missing** or **Partial** rather than omitted — so the gaps are visible, not hidden. Pairs with `plan-phase0-veil-prototype.md` (implementation), the factor table in `spec-galactic-habitability-veil.md`, and the science documents that justify the coefficients.

---

## Conventions & certainty legend

- **Notation:** `M☉/L☉/R☉` solar units; `R` galactocentric radius (kpc); `d` distance; `a` orbital semi-major axis (AU); `[X/H]` abundance in dex vs. solar; `expit(x)=1/(1+e⁻ˣ)`.
- **Certainty ratings** (the analog of the entity schema's provenance):
  - **Fundamental** — an exact physical law within its regime. Trust fully.
  - **Established** — empirical, well-supported, with known scatter. Trust with error bars.
  - **Approximate** — simplified fit or order-of-magnitude. Use, but don't over-read.
  - **Construct** — a *modeling choice*, not physics. Tunable; "true" is not the right word for it.
  - **Partial** — pieces exist; a complete adopted equation must still be assembled from them.
  - **Missing** — no equation yet. Placeholder; requires derivation or a literature adoption decision.
- **Rule:** every value the model asserts should trace to an equation here or to a measured field in `entity.md`. Constructs must remain tunable; Missing/Partial items must not be silently hard-coded as if settled.

---

## 1. Core field model (the veil's mathematical spine)

| ID | Name | Form | Purpose / Use | Certainty |
| --- | --- | --- | --- | --- |
| `EQ-CORE-1` | Log-odds combination | `logit(H) = B₀ + Σᵢ ℓᵢ` | Combine all factor contributions additively in log-odds space so they compound multiplicatively in odds and stay a valid probability | Fundamental (statistics) |
| `EQ-CORE-2` | Logistic transform | `H = expit(logit(H)) = 1/(1+e^(−logit))` | Map combined log-odds back to a habitability probability in (0,1); the veil height | Fundamental |
| `EQ-CORE-3` | Factor contribution | `ℓᵢ = signᵢ · wᵢ · Mᵢ · fᵢ(d) · gᵢ(t)` | Per-factor log-odds term: sign (±), backing weight w∈[0,1], magnitude M, spatial profile f, temporal profile g | **Construct** — the model's defining design choice, not physics |
| `EQ-CORE-4` | Confidence aggregation | `confidence_here = ?` (combine per-factor wᵢ and local data quality) | Produce the observed-vs-speculative shading value per location | **Missing** — no adopted rule yet; TBD (candidate: weighted mean of wᵢ by \|ℓᵢ\|) |

---

## 2. Geometry & coordinates

| ID | Name | Form | Purpose / Use | Certainty |
| --- | --- | --- | --- | --- |
| `EQ-GEO-1` | Distance from parallax | `d(pc) = 1000 / ϖ(mas)` | Convert Gaia/Hipparcos parallax to distance | Fundamental |
| `EQ-GEO-2` | ICRS → galactocentric | rotation + translation (via astropy `Galactocentric`) | Place entities in the galaxy-centered frame all radial factors require | Fundamental (standard astrometry) |
| `EQ-GEO-3` | Cylindrical radius | `R = √(x² + y²)` | Galactocentric radius; the key input to metallicity & density fields | Fundamental |

---

## 3. Stellar physics

| ID | Name | Form | Purpose / Use | Certainty |
| --- | --- | --- | --- | --- |
| `EQ-STAR-1` | Main-sequence lifetime | `t_MS ≈ 10¹⁰ · (M/M☉)^(−2.5) yr` | The hazard clock: when a massive star reaches collapse (`t_collapse = t_birth + t_MS`) | Approximate (exponent 2.5–4 across mass regimes) |
| `EQ-STAR-2` | Stefan–Boltzmann luminosity | `L = 4π R² σ T_eff⁴` | Relate radius, temperature, luminosity; underpins HZ and energy factors | Fundamental |
| `EQ-STAR-3` | Wien's displacement | `λ_peak = b / T,  b = 2.898×10⁻³ m·K` | Spectral peak from surface temperature; drives the energy-availability factor | Fundamental |
| `EQ-STAR-4` | Photon energy / red limit | `E = hc/λ`; oxygenic limit ≈ 1.8 eV ↔ ~700 nm | Whether a star's photons can drive (oxygenic) photosynthesis | Fundamental (limit value Established) |

---

## 4. Chemical evolution (metallicity → habitability)

| ID | Name | Form | Purpose / Use | Certainty |
| --- | --- | --- | --- | --- |
| `EQ-CHEM-1` | Radial metallicity gradient | `[Fe/H](R) ≈ [Fe/H]₀ − 0.06·(R − R₀)` dex, `R₀≈8.2 kpc` | Model metallicity where measured data is absent | Established (gradient −0.05…−0.07, real scatter, non-linear at extremes) |
| `EQ-CHEM-2` | Giant-planet occurrence vs. metallicity | `P(giant) ≈ 10^(2·[Fe/H])` (Fischer–Valenti-type) | The empirical planet–metallicity correlation | Established (for giants; weaker for terrestrials) |
| `EQ-CHEM-3` | Metallicity → habitability mapping (optimum band) | `—` (rises from low-[Fe/H] floor to ~solar, gentle high-[Fe/H] penalty) | Convert metallicity to the veil's positive factor influence | **Partial** — must be assembled from EQ-CHEM-2 plus a chosen upper-penalty; no single adopted form |
| `EQ-CHEM-4` | Metallicity temporal evolution | `[Fe/H](R, t) = ?` | Make the metallicity ridge rise with cosmic time (enrichment) for the time slider | **Missing** — model-dependent (chemical-evolution models); no clean closed form adopted |
| `EQ-CHEM-5` | Radiogenic heat → tectonic longevity | `—` from Th/U/K abundance | Map enrichment to plate-tectonics/dynamo habitability | **Missing** — research-level; no adopted equation |

---

## 5. Habitable zone & planetary quantities

| ID | Name | Form | Purpose / Use | Certainty |
| --- | --- | --- | --- | --- |
| `EQ-HZ-1` | Insolation (Earth-relative) | `S/S⊕ = (L/L☉) / (a/AU)²` | Stellar flux a planet receives; habitability proxy | Fundamental |
| `EQ-HZ-2` | HZ boundaries (flux scaling) | `a_in = √[(L/L☉)/S_in]`, `a_out = √[(L/L☉)/S_out]`, `S_in≈1.1, S_out≈0.35` | Habitable-zone edges from luminosity | Established (simple form; Kopparapu polynomials more rigorous) |
| `EQ-HZ-3` | Equilibrium temperature | `T_eq = T_star·√(R_star/2a)·(1−A)^(1/4)` | Planet climate regime (albedo A assumed ~0.3) | Fundamental (given albedo assumption) |
| `EQ-HZ-4` | Orbital period (Kepler III) | `P(yr)² = a(AU)³ / (M/M☉)` | Derive period from orbit (M_star ≫ M_planet) | Fundamental |

---

## 6. Hazard physics

| ID | Name | Form | Purpose / Use | Certainty |
| --- | --- | --- | --- | --- |
| `EQ-HAZ-1` | Supernova lethality vs. distance | ozone depletion ∝ 1/d²; kill radius `r_k ≈ 8–10 pc` (up to ~50 pc) | Depth/reach of a supernova dip | **Partial** — empirical kill radii exist; no single agreed closed-form lethality(d) |
| `EQ-HAZ-2` | GRB lethal fluence | `Φ_lethal ≈ 100 J/m²` → extinction-grade at ~1–2 kpc (typical), ~5000 ly (large) | Reach of a beamed long-GRB dip | Established (threshold) / Approximate (range) |
| `EQ-HAZ-3` | GRB rate per volume/time | `R_GRB(R,t) ∝ SFR(R,t) · f_metallicity([Fe/H])` | Statistical hazard-density field at galactic scale; epoch dependence | **Partial** — semi-empirical (Piran–Jimenez); needs a parametrization adopted |
| `EQ-HAZ-4` | Survival probability (Poisson) | `S = exp(−λ · τ)`, λ = local lethal-event rate, τ = time for complex life | The hazard-aware Drake multiplier: chance a world is not sterilized in time τ | Established framework / inputs Approximate |
| `EQ-HAZ-5` | Beaming duty factor | `f_beam = Ω_jet / 4π` (few-degree jets) | Down-weight GRB contribution: only targets in the jet are hit | Established (geometry) / jet angle Approximate |

---

## 7. Spatial & temporal profiles (modeling constructs)

| ID | Name | Form | Purpose / Use | Certainty |
| --- | --- | --- | --- | --- |
| `EQ-PROF-1` | Disk density profile | `n(R,z) = n₀·exp(−(R−R₀)/h_R)·exp(−\|z\|/h_z)`, `h_R≈2.5, h_z≈0.3 kpc` | Statistical stellar-density hazard field (crowding, SN/GRB rate scaling) | Established (double-exponential; thin+thick actually two components) |
| `EQ-PROF-2` | Point-hazard falloff | `f(d) = min(1, r_k²/(d²+ε))` with hard cutoff at ~5·r_k | Local-regime spatial profile of an individual hazard | **Construct** (physical input = r_k from EQ-HAZ-1) |
| `EQ-PROF-3` | Hazard temporal ramp | `g(t) = clip((t−t_b)/(t_c−t_b),0,1)³` for t<t_c | Dip deepening as a massive star nears collapse | **Construct** (shape chosen; timing from EQ-STAR-1) |
| `EQ-PROF-4` | Post-collapse decay | `g(t) = exp(−(t−t_c)/τ_decay)` for t≥t_c | Supernova spike then remnant-hazard fade | **Construct** |

---

## 8. Energy-for-life (constructive factors)

| ID | Name | Form | Purpose / Use | Certainty |
| --- | --- | --- | --- | --- |
| `EQ-ENERGY-1` | Photosynthetic viability from spectrum | `—` (photon flux above the ~1.8 eV / 700 nm limit, per stellar SED) | Positive factor: is usable photosynthetic energy available at this star? | **Partial** — exergy-based bounds exist in literature; no simple adopted equation |
| `EQ-ENERGY-2` | Stellar-longevity bonus | function of `t_MS` (EQ-STAR-1): longer MS → more time for life | Positive factor rewarding long-lived (cool) stars | **Construct** (uses Fundamental input) |

---

## Equations we do NOT yet have (explicit gap list)

These are called out so nothing is silently faked. Each needs either a derivation or a documented literature-adoption decision before it drives the veil beyond a placeholder:

- **`EQ-CORE-4` Confidence aggregation** — how to turn per-factor backing weights + data quality into a single per-location confidence. *Missing.*
- **`EQ-CHEM-3` Metallicity → habitability mapping** — the optimum-band curve. *Partial* (have giant-planet occurrence; need the full habitability curve and the high-metallicity penalty).
- **`EQ-CHEM-4` Metallicity temporal evolution `[Fe/H](R,t)`** — required for a physically honest time slider on the metallicity ridge. *Missing.*
- **`EQ-CHEM-5` Radiogenic heat → tectonic/habitability** — mapping Th/U/K to long-term habitability. *Missing.*
- **`EQ-HAZ-1` Supernova lethality(d)** — a single agreed closed form beyond empirical kill radii. *Partial.*
- **`EQ-HAZ-3` GRB rate `R_GRB(R,t)`** — a parametrization to adopt from Piran–Jimenez-type work. *Partial.*
- **`EQ-ENERGY-1` Photosynthetic-energy availability** — a simple usable equation from stellar SED. *Partial.*

---

## Minimum equation set for Phase 0

To run the Phase 0 prototype, only these are strictly required: `EQ-CORE-1/2/3` (the field), `EQ-GEO-1/2/3` (placement), `EQ-STAR-1` (the hazard clock), `EQ-CHEM-1` (modeled metallicity) with a **stand-in** for `EQ-CHEM-3` (a hand-tuned optimum band, flagged Construct), `EQ-PROF-1/2/3/4` (the fields and time behavior). Everything marked Missing/Partial can be represented by a clearly-labeled placeholder in Phase 0 and upgraded to a defensible form as the research track supplies it.
