# Factors v2 — Specification for The Drake Display

> **Status: Proposed.** Supersedes `factors.md` (v1) once accepted. Adopting it requires **ADR-013 (three-term log-space model)**, because it replaces v1's single log-odds sum with three terms that combine additively in log space. That extends, and does not violate, the standing "log-odds over linear summation" principle. Pairs with `entity-effects-matrix.md`, `entity.md`, `equations-core.md`, `equations-provisional.md`, and `spec-galactic-habitability-veil.md`. Appendix A holds constants. Appendix B is the derivation map. **Part II** justifies every departure from v1. **Part III** lists candidate factors this version still omits.
>
> **Citation note:** literature references are given from recall to anchor values and tiers. Verify each one against the paper before it is quoted in research docs or the manuscript.

---

# Part I — Specification

## 0. What the veil displays (endpoint definition)

v1 never stated what its probability *is a probability of*. That made every weight and the implied 0.5 prior uninterpretable. v2 fixes the target first.

**Definition.** `P(x, t | E)` is the probability that a randomly selected star system at position `x` and cosmic time `t`:
1. hosts a planet capable of supporting a biosphere of endpoint class `E`, **and**
2. has been continuously eligible for long enough to reach `E`, **and**
3. has not had that trajectory reset by an external event during the window `τ_E` that `E` requires.

It is **not** the probability that life exists. The abiogenesis term (`f_l` in Drake) is unconstrained by any data, so including it would put an arbitrary constant in front of every value on the veil. The veil maps *habitability potential*. `f_l` belongs to the narrative layer, not the model.

**Endpoint classes** (user-selectable toggle, default `E3`):

| Class | Meaning | Required window `τ_E` | Tier |
|---|---|---|---|
| `E1` | Surface liquid water possible now | 0 | Established (definition) |
| `E2` | Persistent microbial biosphere | ~0.5 Gyr (0.1–1) | Approximate |
| `E3` | Complex multicellular life | ~4 Gyr (3–5) | Contested (n = 1, Earth precedent; Lineweaver et al. 2004 convention) |

**Display modes:**
- **Per-system probability `P`** (default): "how good is a typical system here?"
- **Areal density `N = n_*(x,t) · P`**: "where are habitable systems most numerous?" These two maps disagree sharply. The inner disk can host the most habitable systems *by count* while having lower *per-system* odds (Gowanlock et al. 2011). Both are legitimate questions, and the veil must label which one it is showing.

---

## 1. The model

### 1.1 Three terms, combined in log space

```
P(x,t|E) = σ(ℓ_env) · T · S

ln P = ln σ(ℓ_env) + ln T + ln S
```

| Term | Question it answers | Form | Combination rule |
|---|---|---|---|
| **A: Environment** `σ(ℓ_env)` | Given the star and its surroundings, could a suitable planet exist here? | log-odds | additive in logit, then logistic |
| **T: Time eligibility** `T` | Has this system existed long enough, and is its star still alive? | probability | multiplicative |
| **B: Survival** `S` | Has nothing reset the trajectory during `τ_E`? | log-survival | additive in `ln S` |

The split exists because these are three different kinds of quantity. **Evidence** about a static state combines in log-odds. **Eligibility fractions** multiply. **Destructive stochastic processes** combine as Poisson survival. v1 forced all three through one logit sum (see Part II, D1).

### 1.2 Term A — environment (log-odds)

```
ℓ_env(x,t) = ℓ₀(host) + Σ_j  w_j · M_j · φ_j(x,t)
```

- **`ℓ₀(host)` — the intercept.** This is the logit of the baseline probability that a system in the **reference population** has at least one rocky planet in its habitable zone. Assuming Poisson-distributed planet counts: `ℓ₀ = logit(1 − e^(−η⊕(T_eff)))`. The reference population is the Kepler field: solar-neighborhood dwarfs of near-solar metallicity.
- **`φ_j ∈ [−1, +1]` — signed, dimensionless profile.** It is **defined to be 0 at reference conditions**. Monotone-positive factors use `[0, 1]`, monotone-negative factors use `[−1, 0]`, and band factors use the full range. There is no separate sign field and no `∩` type. Shape lives entirely in `φ`.
- **`M_j` — effect size in nats.** This is the log-odds ratio at full exposure (`|φ| = 1`). It has physical meaning. For example, `M = ln 3 ≈ 1.1` means full exposure triples or thirds the odds. Every `M` carries a central value **and a range** (see §1.5).
- **`w_j ∈ [0, 1]` — credibility shrinkage.** This shrinks the effect toward "no effect" in proportion to how weakly the evidence supports the effect *existing at all*. It is **not** an uncertainty bar. Uncertainty in the effect's *size* is carried by the `M` range. The effective push on the veil is always `w·M`. Both numbers are kept so that "how big if real" stays distinguishable from "how sure it is real."

### 1.3 Term T — time eligibility (probability)

```
T(x,t|E) = Pr[ τ_E + t_settle ≤ age_* ≤ t_MS,* − t_margin ]
```

At **stellar-property** scale, this is evaluated against the star's age posterior. Ages are Inferred with 30–50% error, so T is an integral over the age PDF, not a step function.

At **galactic-smooth** scale, it is the fraction of the local stellar population that is old enough but still on the main sequence. It is computed from the local star-formation history `SFR(R, t')` and the IMF:

```
T(R,t) = ∫∫ IMF(m) · SFR(R, t−a) · 1[τ_E ≤ a ≤ t_MS(m)] dm da   /   ∫∫ IMF(m) · SFR(R, t−a) · 1[a ≤ t_MS(m)] dm da
```

With inside-out disk formation, the outer disk is younger, so `T` falls with radius for `E3`. This term is the physically grounded source of an *outer* boundary in the present epoch (§4, `TERM-T`).

### 1.4 Term B — survival (log-survival)

```
ln S(x,t|E) = − Σ_k  w_k · Λ_k(x,t)

Λ_k = ∫_{t−τ_E}^{t}  λ_k(x,t') · κ_{k,E}(dose) dt'
```

- **`λ_k`** is the rate of events of type `k` whose dose reaches `x` (events per Myr).
- **`κ_{k,E}(dose) ∈ [0,1]`** is the probability that one event at that dose **resets endpoint `E`**. This is a dose-response function (§3, `P-DOSE`). It depends on the endpoint. A dose that ends a complex-life trajectory may be irrelevant to a microbial biosphere.
- **`Λ_k`** is the expected number of reset-equivalent events in the window.
- **Recovery is not a separate factor.** It falls out of the window automatically. Once an event slides out of `[t − τ_E, t]`, it stops counting.

**Point sources with identified progenitors** (local zoom) contribute:

```
Λ_src = κ(d) · p_branch · [F_c(t) − F_c(t − τ_E)]
```

Here `F_c` is the CDF of the progenitor's collapse time (Statistical-only tier) and `p_branch` is the probability that the progenitor takes the relevant fate (§2.2).

### 1.5 Uncertainty propagation (mandatory)

Each `M`, `κ_max`, `r_50`, rate normalization, and `τ_E` has a range in Appendix A. The renderer draws `N_mc` joint samples (Phase 0: 32 on the coarse grid). It displays the **median** as veil height and the **90% interval width** on the confidence color channel (blue → purple → red, per `schema-field-definition.md`). This is how Appendix B's implementation rule is satisfied structurally rather than by a single low `w`.

### 1.6 Regimes and the partition rule

The four v1 regimes are retained: **Galactic-smooth**, **Local-point**, **Stellar-property**, and **Global-temporal**.

**New partition rule** (prevents double counting across regimes): smooth hazard fields represent *unresolved* sources only. In any view where a catalog resolves sources of type `k`:

```
λ_k,smooth,effective = λ_k,smooth · (1 − C_k(x, scale))
```

`C_k` is the catalog's completeness for that source type at that location and zoom. Resolved sources then enter as point terms. At galactic zoom `C ≈ 0` and everything is smooth. At local zoom near the Sun, `C_CCSN → ~1` for massive progenitors within a few hundred pc.

---

## 2. Canonical registry

### 2.1 Term A factors (environment, log-odds)

| ID | Name | φ shape | Regime | Inputs | φ / profile | g | M (nats) | M range | w | Tier | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `FAC-BASE` | Intercept: rocky-HZ occurrence | — | Stellar-property / smooth | `teff_k` | `ℓ₀ = logit(1−e^(−η⊕(T_eff)))` | G-STATIC | — | η⊕ 0.15–1.5 | 1.0 | Inferred | Specified |
| `FAC-METAL-FLOOR` | Planet-formation metallicity floor | monotone + | Smooth (stellar-property if `feh` measured) | `feh` or `r_gal_kpc` | `P-RADIAL` → `φ = σ(([Fe/H] − Z_crit(a_HZ))/δ) − 1` | G-ENRICH | 3.0 | 1.5–5.0 | 0.7 | Inferred | Specified (EQ-CHEM-3 now partially closed) |
| `FAC-METAL-HIGH` | Giant-planet HZ disruption at high Z | monotone − | Smooth / stellar-property | `feh` | `φ = −clip(f_GP([Fe/H]) − f_GP(0), 0, 1)/Δf_max` | G-ENRICH | 0.15 | 0.0–0.4 | 0.4 | Contested | Specified (small by construction) |
| `FAC-LOWMASS` | Low-mass host penalty (tidal locking, pre-MS water loss, SED) | monotone − | Stellar-property | `mass_msun` | `φ = −clip((0.6 − m)/0.5, 0, 1)` | G-STATIC | 1.0 | 0.0–3.0 | 0.5 | Contested | Specified |
| `FAC-ACTIVITY` | Excess activity (residual vs mass–age expectation) | signed | Stellar-property | `log_lx_lbol`, `mass_msun`, age | `φ = −clip((obs − expected(m, age))/σ_act, −1, 1)` | G-STATIC (age dependence lives in `expected`) | 0.8 | 0.3–1.5 | 0.4 | Inferred | Placeholder (activity–age relation) |
| `FAC-PLANET-OBS` | Observational update on planets | signed | Local-point | planet fields, completeness `c` | Bayesian replacement of `ℓ₀` (§4) | G-STATIC | rule-based | — | 0.9 | Direct | Specified (where data exist) |
| `FAC-BINARY-STAB` | Dynamical HZ stability in multiples | monotone − | Stellar-property | `a_bin`, `e_bin`, `μ` | `φ = −(HZ fraction inside unstable region)` (Holman & Wiegert 1999) | G-STATIC | 4.0 | 3.0–6.0 | 0.9 | Established physics / Inferred inputs | Specified |
| `FAC-BINARY-FORM` | Close-binary planet-formation suppression | monotone − | Stellar-property | `a_bin` | `φ = −1 if a_bin < ~50 AU, smooth taper to 0 by ~200 AU` | G-STATIC | 1.1 | 0.7–1.6 | 0.7 | Inferred | Specified |
| `FAC-RADIOHEAT` | Radiogenic heat budget / tectonics | signed | Stellar-property / smooth | `abundance_th_u_proxy`, `feh` | `φ = clip(log([Th/U-proxy]/solar)/0.3, −1, 1)` | G-ENRICH (r-process enrichment) | 0.4 | 0.0–1.0 | 0.25 | Gap | Placeholder (EQ-CHEM-5) |

### 2.2 Term B factors (survival hazards, log-survival)

`r_50` is the distance at which one event resets endpoint `E` with probability `κ_max/2`. `n` is the dose-response steepness in distance (§3). `κ_max` values are for the default `E3`. `E2` values are generally one to two orders of magnitude smaller (Appendix A).

| ID | Event | Regime | Rate source | r_50 | n | κ_max (E3) | Branch / beaming | w | Tier | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| `HAZ-CCSN-PT` | Core-collapse SN, identified progenitor | Local-point | `F_c` from EQ-STAR-1 + mass/age posteriors | 10 pc (8–20; tail to 50 for interacting/X-ray-luminous SNe) | 4 | 0.2 (0.05–1.0) | `(1 − p_GRB)` | 0.9 | Statistical-only (timing) / Approximate (dose) | Specified |
| `HAZ-CCSN-FLD` | Core-collapse SN, unresolved | Galactic-smooth | `∝ Σ_SFR(R, φ_arm, t)` via `P-SFR` | as above | 4 | as above | `(1 − p_GRB)` | 0.9 | Statistical-only | Specified |
| `HAZ-SNIA-FLD` | Type Ia SN (never progenitor-identifiable) | Galactic-smooth | `∝ ρ_*(R,z) ⊗ DTD(t^−1)` via `P-MSTAR` | 10 pc (8–20) | 4 | 0.2 (0.05–1.0) | — | 0.8 | Statistical-only | Specified (new) |
| `HAZ-LGRB` | Long GRB / collapsar (includes its own SN Ic-BL near-field term) | Local-point + smooth | CCSN rate × `p_GRB(Z, m)` | on-axis 1.5 kpc (1–3) | 4 | 0.2 (0.05–1.0) | `p_GRB` × `f_beam` (forecast) or sampled axis (scenario) | 0.7 | Statistical-only | Placeholder (EQ-HAZ-3, `p_GRB(Z)`) |
| `HAZ-MERGER` | BNS merger: kilonova (isotropic) + short GRB (beamed) | Local-point (known DNS binaries) + smooth | `∝ ρ_* ⊗ DTD` | kilonova ~10 pc (Approximate); sGRB on-axis ~0.1–0.5 kpc | 4 | 0.2 | sGRB `f_beam` | 0.4 | Approximate | Specified (minor) |
| `HAZ-MAGNETAR` | Magnetar giant flare | Local-point | per-magnetar flare rate | ≲1 pc | 4 | 0.2 | — | 0.3 | Approximate | Specified (negligible in practice) |
| `HAZ-ENCOUNTER` | Stellar flyby destabilizing HZ orbits | Galactic-smooth | `Γ = n_* · σ_enc · v_rel` via `P-MSTAR` | gate at `b < b_crit ≈ 3·a_HZ` | — (step) | 1.0 for E1–E3 within `b_crit` | — | 0.8 | Established physics | Specified (replaces v1 density hazard) |
| `HAZ-AGN` | Galactic-nucleus XUV during active phases | Galactic-smooth | duty cycle × luminosity history of Sgr A* | ~1 kpc in active phase (Contested) | 2 (plain inverse-square on dose) | 0.2 | duty cycle | 0.3 | Contested | Placeholder |
| `HAZ-MOLCLOUD` | Dense-cloud passage (astrosphere compression, dust) | Local-point | cloud catalog × relative velocity | in-cloud only | — | 0.02 (0–0.1) | — | 0.15 | Construct | Construct |

**Fate exclusivity.** A massive progenitor takes one terminal fate, so `HAZ-CCSN-PT` and `HAZ-LGRB` share a progenitor and partition it: CCSN uses `(1 − p_GRB)`, and LGRB uses `p_GRB`. The LGRB term includes the near-field dose of its accompanying broad-lined Ic SN. Failed SNe (direct collapse to a black hole) take a share `p_fail` that contributes no hazard.

### 2.3 Global-temporal effects

No standalone global factor exists in v2. Cosmic-time behavior arises from `Z(R,t)`, `SFR(R,t)`, and DTDs feeding the terms above. Early-universe GRB saturation, for example, emerges from `p_GRB(Z(t))` × high early SFR. It is not added as a separate penalty (Part II, D9).

---

## 3. Profile library

### 3.1 Spatial

- **`P-RADIAL`** — `[Fe/H](R) = [Fe/H]₀ + ∇[Fe/H]·(R − R₀)` (EQ-CHEM-1), with gradient flattening beyond ~12–14 kpc as an uncertainty option. Feeds `FAC-METAL-*` and `FAC-RADIOHEAT`.
- **`P-SFR`** — star-formation surface density `Σ_SFR(R, φ_arm, t)`. The radial envelope peaks in the molecular ring (~4–6 kpc) and is depleted between the central molecular zone and the ring. Arm modulation comes from the BeSSeL loci. **This is where spiral structure enters the model.** Feeds CCSN and LGRB rates. Volume rate density: `Σ_SFR / (2 h_z,young)`, with `h_z,young ≈ 0.05–0.1 kpc`.
- **`P-MSTAR`** — stellar mass density, double exponential (EQ-PROF-1, old `P-DISKDENS`), plus a bulge/bar component inside ~3 kpc. Feeds SN Ia, mergers, encounters, and `n_*` for density mode.
- **`P-DOSE`** — log-logistic dose-response, replacing v1's truncated inverse-square:
  ```
  κ(d) = κ_max / (1 + (d / r_50)^n)
  ```
  Dose scales as `d⁻²`, and biological response is sigmoidal in log dose with Hill slope `β`, so `n = 2β`. The default `n = 4` corresponds to `β = 2`. No hard cutoff is needed. Evaluation is truncated where `κ < 10⁻³ κ_max` for performance only.
  **Effective volume/area for smooth fields** (closed form, valid for `n > 3` and `n > 2` respectively):
  ```
  V_eff = 4π r_50³ · (π/n) / sin(3π/n)        → n=4: ≈ 13.96 r_50³     (use when r_50 ≪ h_z)
  A_eff = 2π r_50² · (π/n) / sin(2π/n)        → n=4: = π² r_50² / 2    (use when r_50 ≫ h_z; GRBs)
  ```
  Smooth hazard rate at `x`: `λ_k · κ̄ = κ_max · (rate density) · V_eff`, or `· A_eff` with surface rate density.
- **`P-BEAMED`** — forecast mode: `P-DOSE × f_beam`, with `f_beam = 1 − cos θ_jet` for a two-sided jet (≈ 0.4% at 5°). Scenario mode: sample a jet axis, and apply full `P-DOSE` inside the cone and zero outside it.
- **`P-AGN`** — dose from the Galactic Center, `∝ L_AGN(t) / R²`, with optional column attenuation.
- **`P-STELLAR`** — evaluated at the star's own cell from its properties.
- **`P-GLOBAL`** — spatially uniform. Retained for future use, unused in v2.

### 3.2 Temporal

- **`G-STATIC`** — constant.
- **`G-COLLAPSE`** — collapse-time distribution `f_c(t)` and CDF `F_c(t)`, from `t_MS(m)` convolved with mass and age posteriors. **Forecast mode** uses the expectation (smooth). **Scenario mode** samples one collapse time and renders a sharp event. This replaces v1's `G-RAMP-SPIKE-DECAY` (Part II, D7).
- **`G-WINDOW`** — the survival-window operator `∫_{t−τ_E}^{t}`. It replaces `G-RECOVERY`.
- **`G-ENRICH`** — `Z(R,t)` from an inside-out chemical-evolution model (EQ-CHEM-4; **placeholder**, hold at present-day gradient in Phase 0).
- **`G-SFH`** — `SFR(R,t)`: inside-out disk growth. It feeds `TERM-T` and CCSN/LGRB rates.
- **`G-DTD`** — delay-time distribution `∝ t⁻¹` for t > ~40 Myr (SN Ia, BNS mergers).
- **`G-ACTIVITY-AGE`** — expected activity versus mass and age, used only to residualize `FAC-ACTIVITY`.
- **`G-DUTY`** — AGN episodic duty cycle.
- **`G-TRANSIENT`** — bounded passage window (molecular clouds).

Removed: `G-RAMP-SPIKE-DECAY`, `G-RECOVERY`, `G-FLARE-DECLINE`, `G-ENRICH-INV` (each is now derived or subsumed).

---

## 4. Per-factor notes

- **`FAC-BASE`.** η⊕ for Sun-like stars from Kepler DR25 is roughly **0.4–0.6 rocky HZ planets per star**, with error bars spanning about 0.15–1.5 (Bryson et al. 2021). That gives `P(≥1) ≈ 0.33–0.45`, so `ℓ₀ ≈ −0.7 to −0.2`. This is anchored, not assumed. M-dwarf η⊕ is comparable or higher. The low-mass penalty therefore lives in `FAC-LOWMASS`, as "HZ planet exists but may not be habitable," not in occurrence.
- **`FAC-METAL-FLOOR`.** The critical metallicity for planet formation scales as `Z_crit ≈ −1.5 + log₁₀(a/AU)` dex (Johnson & Li 2012). Above roughly −0.5 dex, **small-planet occurrence is nearly flat in metallicity** (Buchhave et al. 2012, 2014). Only giant and sub-Neptune occurrence rises steeply (`∝ 10^(2[Fe/H])`, Fischer & Valenti 2005). Consequence: with a −0.06 dex/kpc gradient, the present-day disk spans about −0.5 to +0.4 dex, and **the floor barely binds anywhere in today's disk**. It matters in early epochs, the thick disk, and the halo. See Part II, D4 for what this does to the habitable annulus.
- **`FAC-METAL-HIGH`.** This is the Lineweaver (2001) migrating-giant argument, quantified. Hot-Jupiter occurrence is ~1% at solar metallicity and ~5–6% at +0.4 dex. Even if every such system lost its HZ planet, the penalty is `ln(1 − 0.05) ≈ −0.05` nats. Including eccentric warm and cold giants can raise that by a few times at most. Hence `M = 0.15`. The upper side of v1's "optimum band" is real but nearly invisible.
- **`TERM-T` (not a registry row; computed per §1.3).** This term carries most of v1's `FAC-LONGEVITY` and `FAC-FGK` content correctly. Longevity matters only as a **gate** (`t_MS ≥ τ_E`), not as a monotone bonus. For `E3`, stars above ~1.2–1.3 M☉ fail the gate outright.
- **`FAC-PLANET-OBS`.** This is a rule, not a weight:
  - **Rocky HZ planet detected:** replace `P(planet exists)` with ~1. Remaining habitability uncertainty (atmosphere, water) sets `P_env` to a ceiling parameter `p_hab|planet` (default 0.5, range 0.2–0.9, Contested).
  - **Survey non-detection with completeness `c`:** `P' = P(1 − c) / (1 − P·c)`. If `c` is unknown, set `c = 0` and treat the non-detection as uninformative.
  - **Giant planet detected in or straddling the HZ:** apply the Holman–Wiegert-style exclusion as for binaries, with `φ = −1` in the extreme case.
- **`FAC-BINARY-STAB`.** Critical semimajor axes are closed-form (Appendix A). If multiplicity is unknown, use the expected value under the mass-dependent multiplicity prior (Raghavan et al. 2010; Duchêne & Kraus 2013). Do not use zero.
- **`FAC-ACTIVITY`.** Only the residual counts. Mass-driven activity is already priced into `FAC-LOWMASS`, and age-driven activity is already priced into `TERM-T`. Counting raw activity would triple-count the same physics.
- **Hazard lethality (`κ_max`) — the most consequential contested parameter in v2.** The ~10 pc "kill radius" in the literature corresponds to **mass-extinction-level** ozone depletion (roughly a doubling of biologically active UV; Gehrels et al. 2003). It does not correspond to sterilization or to an irreversible end of complex life. Earth's record shows mass extinctions are setbacks, not resets. Default `κ_max = 0.2` for `E3` and ~0.002 for `E2`. Set `κ_max = 1` to reproduce the Lineweaver/Gowanlock convention. See the Earth-consistency test in §5.

---

## 5. Calibration and acceptance tests

1. **Reference neutrality (by construction).** A Sun-like star at `R₀` with `[Fe/H] = 0`, single, quiescent, with no detection data, gives `Σ w·M·φ ≈ 0`, so `P_env = σ(ℓ₀)`.
2. **Anchor A, data.** `FAC-METAL-FLOOR` must reproduce the observed lack of metallicity dependence in small-planet hosts above −0.5 dex.
3. **Anchor B, data.** Integrating `P-SFR` and `P-MSTAR` hazard fields over the disk must give a total Galactic SN rate of ~1.5–2.5 per century, with Ia fraction ~0.2–0.3 (Rozwadowska et al. 2021 and earlier estimates).
4. **Anchor C, cross-model (not data).** Under matching assumptions, the radial profile of `P` should broadly resemble Lineweaver et al. 2004 and Gowanlock et al. 2011. Any disagreement must be explained by a named assumption.
5. **Earth-consistency check.** With nearby-SN rates of order 1–2 per Gyr within ~8–10 pc (Gehrels et al. 2003), the Sun accumulates roughly 4–8 expected events over its 4 Gyr `E3` window. At `κ_max = 1`, that gives `S_☉ ≈ e⁻⁴` to `e⁻⁸`, which would make the Sun a 1-in-50 to 1-in-3000 survivor. Observer selection guarantees our survival in the sample, so this is not decisive. But a model that labels its only known example a large fluke should be distrusted. With the default `κ_max = 0.2`, `S_☉ ≈ 0.2–0.45`.
6. **Sun-in-favorable-region test (demoted).** Passing it is **necessary but not confirming**, because of observer selection. Do not tune toward it.

---

# Appendix A — Constants and parameters

v1 values are retained unless noted. New or changed rows are marked **★**.

| Symbol | Meaning | Value | Range | Tier | Used by |
|---|---|---|---|---|---|
| `R₀` | Sun's galactocentric radius | 8.2 kpc | ±0.1 | Established | coords, profiles |
| `z₀` | Sun's height above plane | 0.02 kpc | ±0.005 | Established | coords |
| `∇[Fe/H]` | Radial metallicity gradient | −0.06 dex/kpc | −0.05 to −0.07; flattening beyond ~12–14 kpc | Established | P-RADIAL |
| `[Fe/H]₀` | Metallicity at `R₀` | 0.0 | ±0.1 | Established | P-RADIAL |
| `h_R` | Stellar disk scale length | 2.5 kpc | 2.0–3.0 | Established | P-MSTAR |
| `h_z` | Thin-disk scale height (old stars) | 0.3 kpc | thick disk ~0.9 | Established | P-MSTAR |
| ★ `h_z,young` | Scale height of massive young stars | 0.07 kpc | 0.05–0.1 | Established | P-SFR |
| ★ `R_SFR,peak` | Molecular-ring SFR peak | 5 kpc | 4–6 | Approximate | P-SFR |
| ★ `η⊕` | Rocky HZ planets per FGK star | 0.5 | 0.15–1.5 | Inferred | FAC-BASE |
| ★ `τ_E2`, `τ_E3` | Endpoint windows | 0.5, 4 Gyr | 0.1–1; 3–5 | Approximate; Contested | TERM-T, G-WINDOW |
| ★ `Z_crit(a)` | Formation floor | −1.5 + log₁₀(a/AU) dex | ±0.3 | Inferred | FAC-METAL-FLOOR |
| ★ `δ` | Floor transition width | 0.25 dex | 0.15–0.4 | Approximate | FAC-METAL-FLOOR |
| ★ `f_GP(Z)` | Giant-planet occurrence | 0.03·10^(2[Fe/H]) | normalization 0.02–0.06 | Established | FAC-METAL-HIGH |
| ★ `p_hab|planet` | Habitability given a confirmed rocky HZ planet | 0.5 | 0.2–0.9 | Contested | FAC-PLANET-OBS |
| ★ multiplicity | Fraction of multiple systems | ~0.46 (FGK), ~0.27 (M) | ±0.05 | Established | FAC-BINARY-* |
| ★ HW99 S-type | `a_c/a_b = 0.464 − 0.380μ − 0.631e + 0.586μe + 0.150e² − 0.198μe²` | — | fit validity 0.1 ≤ μ ≤ 0.9, 0 ≤ e ≤ 0.8 | Established | FAC-BINARY-STAB |
| ★ HW99 P-type | `a_c/a_b = 1.60 + 5.10e − 2.22e² + 4.12μ − 4.27eμ − 5.09μ² + 4.61e²μ²` | — | same | Established | FAC-BINARY-STAB |
| ★ `a_bin,supp` | Close-binary suppression scale | 50 AU | 30–100 | Inferred | FAC-BINARY-FORM |
| `r_50,SN` | SN reset distance (was `r_k,SN`) | 10 pc | 8–20 (tail 50) | Approximate | HAZ-CCSN, HAZ-SNIA |
| `Φ_lethal` | GRB lethal fluence | 100 J/m² | — | Established | HAZ-LGRB |
| `r_50,GRB` | On-axis GRB reset distance | 1.5 kpc | 1–3 | Approximate | HAZ-LGRB |
| `θ_jet` | GRB jet half-angle | 5° | 2–10° | Approximate | P-BEAMED |
| ★ `n` | Dose-response steepness (distance) | 4 | 3–6 | Approximate | P-DOSE |
| ★ `κ_max,E3` | Reset probability per full-dose event | 0.2 | 0.05–1.0 | **Contested** | all HAZ |
| ★ `κ_max,E2` | Same, microbial endpoint | 0.002 | 0–0.02 | Contested | all HAZ |
| ★ `p_GRB` | Collapsar fraction of massive-star deaths | ~0.5% at Z ≲ 0.3 Z☉ | 0.1–1%; strongly suppressed above ~0.5 Z☉ | Statistical-only | HAZ-LGRB |
| ★ `p_fail` | Failed-SN fraction | 0.15 | 0.05–0.3 | Inferred | HAZ-CCSN |
| ★ `R_SN,MW` | Total Galactic SN rate | 2 /century | 1.5–2.5 | Inferred | Anchor B |
| ★ `f_Ia` | Ia share of SN rate | 0.25 | 0.2–0.3 | Inferred | HAZ-SNIA |
| ★ `b_crit` | Flyby destabilization impact parameter | 3·a_HZ | 2–5·a_HZ | Established physics | HAZ-ENCOUNTER |
| `t_MS,☉` | MS-lifetime normalization | 1.0×10⁴ Myr | — | Approximate | EQ-STAR-1 |
| `α_MS` | MS-lifetime mass exponent | −2.5 | −2.5 to −4 | Approximate | EQ-STAR-1 |
| `S_inner`, `S_outer` | HZ flux bounds | 1.1, 0.35 S⊕ | 1.0–1.5; 0.32–0.53 | Established | EQ-HZ-2 |
| `b_Wien` | Wien constant | 2.898×10⁻³ m·K | exact | Fundamental | EQ-STAR-3 |
| `E_oxy` | Oxygenic photon-energy limit | 1.8 eV | — | Established | EQ-STAR-4 |
| ~~`R_inner`~~ | ~~Inner penalty onset~~ | removed | — | — | — |

# Appendix B — Derivation map

v1 rows are retained. New rows:

| Derived quantity | From | Via | Tier | Caveat |
|---|---|---|---|---|
| ★ Baseline intercept `ℓ₀` | `T_eff` | η⊕ occurrence fits | **Inferred** | Kepler-field reference population; extrapolation to other R is an assumption |
| ★ Time eligibility `T` | age posterior / SFH + IMF | §1.3 | **Inferred** (star) / **Statistical-only** (field) | SFH(R,t) model-dependent |
| ★ Collapsar fraction `p_GRB` | metallicity, mass | host-galaxy statistics | **Statistical-only** | never deterministic per star |
| ★ Reset probability `κ` | dose | biological dose-response | **Gap** (no validated mapping from fluence to lineage extinction) | single most contested parameter |
| ★ Binary stability | orbital elements | HW99 | **Direct** when elements known; **Statistical-only** under the multiplicity prior | — |
| ★ Survey completeness `c` | survey design | injection–recovery | **Inferred** | default 0 when unknown |
| Metallicity→habitability curve | metallicity | EQ-CHEM-3 | **Inferred** (floor) / **Contested** (high side) | was Gap in v1; now partially closed |

---

# Part II — Justification: v1 → v2

Each decision states what changed, why, and how confident I am. Where v2 contradicts something I told you in the review, I say so explicitly.

### D1. Single log-odds sum → three terms in log space *(high confidence; reverses part of my review)*
In the review I told you the additive log-odds architecture was right and not to second-guess it. That was too generous. Log-odds additivity is the correct way to combine **independent evidence about a static state**. A supernova is not evidence that a region is uninhabitable. It is a **process that destroys habitability** with some probability per event. Processes like that combine as Poisson survival, `S = exp(−Σ Λ)`. In v1, a hazard term in the logit could be offset by enough positive terms, so "great metallicity" could literally buy back a sterilizing event. That is a category error. In v2, `S` multiplies the result, so no environment term can rescue a dead system. That is the veto behavior you described in your first message, now in a mathematically honest form. Lineweaver et al. 2004 and Gowanlock et al. 2011 both use this multiplicative structure. The log-space additivity principle survives: all three terms add in `ln P`.

### D2. Define the endpoint before defining weights *(high confidence)*
v1's numbers had no referent: probability of *what*, over *what window*? The `E1/E2/E3` toggle makes `τ_E` explicit. `τ_E` controls both time eligibility and how long a hazard keeps suppressing the veil. Excluding `f_l` keeps an unconstrained guess out of the map entirely, rather than smearing it into every cell.

### D3. Add an anchored intercept *(high confidence; corrects my review)*
I said the base rate was "almost certainly much lower than 50%." For the rocky-HZ-planet endpoint, that was wrong. η⊕ of ~0.4–0.6 gives `P(≥1)` of ~0.33–0.45, so v1's implicit 0.5 was not wildly off. The real defect was not the value but the **absence of a referent**: nothing tied zero logit to any population. v2 anchors `ℓ₀` to η⊕ and defines every `φ` as zero at the Kepler-field reference. That turns every `M` into an interpretable log-odds ratio relative to a measured population.

### D4. Split `FAC-METAL` into floor and high-Z terms, and demote the keystone *(high confidence in the physics; this is the most consequential change)*
v1's `∩` band with `w = 0.9` conflated two claims of very different strength. The floor (planets need metals to form) is solid, but quantitatively it sits near −1 to −1.5 dex. Above about −0.5 dex, rocky-planet occurrence is nearly flat. The high-Z decline is real but tiny (D4 math in §4: ~0.05–0.15 nats). **Consequence: in the present-day disk, metallicity barely shapes the habitable annulus at all.** The annulus v1 produced was mostly an artifact of a hand-tuned band, which is why it could only be validated against a single point. In v2:
- the **inner** boundary comes from hazards (SN/GRB rates following SFR, encounters following stellar density);
- the **outer** boundary for `E3` comes from `TERM-T` (an inside-out disk is younger outside);
- metallicity matters mainly **over cosmic time**, via `G-ENRICH` and the GRB metallicity dependence.

This also takes seriously a criticism the GHZ concept already faces: Prantzos (2008) argued the canonical GHZ is weakly constrained and much of the disk may be habitable. **Bias flag:** "the galactic habitable zone is an annulus" is more popular-science consensus than robust result. Let the model tell you whether an annulus exists. Don't build one in.

### D5. Replace `w`-as-uncertainty with explicit ranges and Monte Carlo *(high confidence)*
v1 used one number, `w`, both to discount weakly supported factors and to express uncertainty. Shrinkage toward zero is not uncertainty. For hazards, shrinkage is systematically **optimistic**: a poorly understood hazard gets treated as absent. v2 keeps `w` for "does this effect exist," uses `M`/`κ` ranges for "how big," and renders the spread. That is the only way to satisfy Appendix B's rule that Statistical-only and Gap quantities must have visible uncertainty.

### D6. Decompose the triple-counted "inner galaxy is dangerous" *(high confidence)*
`FAC-DENSITY`, `FAC-AGN`, and `P-INNER` all penalized small R with no stated mechanism, three times over. v2 keeps only mechanisms:
- CCSN rate follows **SFR, not stellar density**. SFR peaks in the molecular ring, not the center. v1 used the wrong tracer.
- Ia and merger rates follow stellar mass with a delay-time distribution.
- Encounters follow `n_*` with explicit cross-section physics.
- The AGN term is episodic and low-credibility.

The arbitrary logistic step at 2.5 kpc is deleted.

### D7. Replace `G-RAMP-SPIKE-DECAY` with a collapse-time distribution *(high confidence)*
v1's dip "deepens over the progenitor's main-sequence life." A progenitor emits no lethal dose before collapse, so the ramp was really a disguised expression of uncertainty about *when* collapse happens. v2 makes this explicit as `F_c(t)`. **Forecast mode** renders the expectation, honoring the Statistical-only tier. **Scenario mode** samples one collapse time and gives you the sharp, dramatic event for the 4D demo. You keep the visual spectacle, and it is now labeled correctly as one realization rather than a prediction.

### D8. Fate exclusivity for SN / GRB *(high confidence; executes my review's point 4)*
A progenitor dies once. `(1 − p_GRB)` and `p_GRB` partition it. `p_GRB` is strongly metallicity-suppressed, so the GRB term naturally concentrates in metal-poor regions and early epochs.

### D9. Fold `FAC-EPOCH-GRB` into `HAZ-LGRB` via `Z(t)` *(high confidence)*
A standalone early-universe penalty plus a metallicity-dependent GRB rate would count the same physics twice. With `p_GRB(Z(R,t))` × `SFR(R,t)`, early GRB saturation emerges on its own, and the veil rises over cosmic time for the right reason.

### D10. Absorb `FAC-RECOVERY` into the survival window *(high confidence)*
"Time since last sterilization" is exactly what `∫_{t−τ_E}^{t}` measures. Keeping it as a separate positive factor would double count the hazard history and add an unconstrained construct.

### D11. Reinterpret lethality: `κ_max` and the Earth-consistency test *(medium confidence; flagged as the most contested parameter)*
The literature's kill radii describe mass-extinction-scale damage. Earth survived several such events, and probably some SNe and possibly a GRB, within its complex-life window. Treating every one as a full reset makes Earth a 1-in-thousands survivor under this model's own rates. Default `κ_max = 0.2` is a judgment call, so it carries a wide range and a toggle back to the literature convention. **Bias flag:** popular accounts routinely equate "within 10 pc" with "sterilized." They are not the same.

### D12. Split `FAC-BINARY` and upgrade it *(high confidence; executes my review's point 6)*
Stability is closed-form dynamics (HW99), so it is near-gate strength when the HZ is unstable. Formation suppression in close binaries is an observed effect, roughly a factor of 3 (Kraus et al. 2016). v1's single `Construct, w = 0.3` row undersold both.

### D13. Replace `FAC-FGK` and `FAC-LONGEVITY` *(medium-high confidence)*
Both keyed on stellar mass, alongside `FAC-FLARE` and the HZ factor. That is four correlated terms summed as if independent. v2 gives each mass-dependent effect exactly one home:
- **occurrence** → `ℓ₀(T_eff)`
- **lifetime** → `TERM-T` (as a gate, not a monotone bonus; longevity beyond `τ_E` adds nothing to habitability now)
- **M-dwarf habitability risks** → `FAC-LOWMASS`
- **anomalous activity** → `FAC-ACTIVITY` (residual only)

### D14. `FAC-PLANET-HZ` → `FAC-PLANET-OBS` *(high confidence)*
A detected planet is not one more weighted vote. It **replaces the prior**. Non-detections are weak evidence, but they are evidence, and the completeness formula prices them correctly. Detected HZ giants are evidence against rocky HZ planets. v1 ignored both.

### D15. Spiral arms, molecular clouds, magnetars, kilonovae *(medium confidence)*
- **Spiral arms** enter through `P-SFR` arm modulation, not as a free-standing penalty. That removes double counting with SN rates.
- **Molecular clouds** stay as a near-negligible construct.
- **Magnetars** are kept for completeness. Their effective range is ≲1 pc, which is negligible at any realistic density.
- **Mergers** get a proper source: known double-neutron-star binaries with computed merger times (e.g., Hulse–Taylor merges in ~300 Myr). That gives you a rare, real, catalog-driven point hazard for local zoom.

**Net factor count:** v1 had 17 rows. v2 has 9 environment rows (including the intercept), 1 computed time term, and 9 hazard rows. That is slightly more rows, but fewer *independent free knobs*, because three v1 factors are now derived and every correlated cluster is collapsed to one home per mechanism.

---

# Part III — Candidate factors not yet in v2

Ordered roughly by expected impact. **Recommendation** is one of *add now*, *add later*, *document as scope limit*, or *reject*.

| # | Candidate | Mechanism | Likely home | Tier | Recommendation |
|---|---|---|---|---|---|
| 1 | **Stellar orbits and radial migration** | Stars migrate kpc over Gyr (Sellwood & Binney 2002). A system's hazard history is integrated along its orbit, not at its current `x`. The Sun probably formed 1–2 kpc further in. This undercuts any fixed-point survival integral for `E3`. | Model-level: `G-WINDOW` evaluated along orbits (Phase 0: circular orbits; later: epicyclic plus a migration diffusion kernel) | Established (that migration occurs) | **Add later; document now.** This is the largest structural limitation in v2. |
| 2 | **Non-HZ habitats (subsurface oceans)** | Europa- and Enceladus-type ocean worlds don't need the HZ and may outnumber surface-water worlds. The whole model is HZ-centric. | Endpoint scope, possibly an `E2-sub` variant | Inferred | **Document as scope limit**; consider for narrative. |
| 3 | **Birth-cluster environment** | OB-star photoevaporation truncates disks. Early flybys. ²⁶Al from nearby massive stars heats planetesimals and **dries them**, possibly controlling water budgets (Lichtenberg et al. 2019). | Term A (`FAC-BIRTHENV`), keyed to birth-SFR density | Inferred / Contested | **Add later.** |
| 4 | **Refractory and volatile ratios (Mg/Si, Fe/Mg, C/O)** | Sets mantle mineralogy, core fraction, and possibly tectonic regime and water. Varies with Galactic chemical evolution independently of [Fe/H]. | Term A, alongside `FAC-RADIOHEAT` | Contested | **Add later** (low `w`). |
| 5 | **Impact flux from Oort-cloud perturbation** | Galactic tide (strongest in denser regions) and stellar encounters trigger comet showers. | Term B (`HAZ-IMPACT`), rate from `P-MSTAR` + tide | Inferred mechanism / Contested magnitude | **Add later.** |
| 6 | **Continuously habitable zone** | The HZ moves outward as the star brightens. A planet must stay in it for `τ_E`. | Fold into `TERM-T` (`t_margin` becomes CHZ-derived) | Established | **Add now** (small change). |
| 7 | **OB associations, Wolf–Rayet winds, X-ray binaries / microquasars** | Local UV, X-ray, and wind hazards in star-forming regions. | Term B point hazards | Approximate | **Add later**, local zoom only. |
| 8 | **Vertical structure and thick-disk/halo populations** | The 2D display collapses `z`. Thick-disk and halo stars are old and metal-poor with different hazard exposure. | Population mixture per cell | Established | **Document as scope limit**; optional population toggle. |
| 9 | **Galactic history events** | Gaia–Enceladus merger (~10 Gyr ago); Sagittarius dwarf passages possibly triggering star-formation bursts; bar formation. | `G-SFH` perturbations | Inferred | **Add later** for time-slider fidelity. |
| 10 | **ISM/dust column shielding** | Attenuates X-ray/UV hazard doses in the plane. Gamma rays and cosmic rays are largely unaffected. | `P-DOSE` attenuation term | Established physics | **Add later.** |
| 11 | **Cosmic-ray flux variation (arm passages, Local Bubble)** | Ionization and atmospheric chemistry. The climate-forcing (cloud-seeding) version is weak. | Term B, sublethal | Contested | **Add later, low `w`. Bias flag:** the Svensmark cosmic-ray–cloud–climate link is largely unsupported by subsequent work (e.g., CERN CLOUD results). Do not let it in as an Established mechanism. |
| 12 | **Giant-planet architecture beyond the HZ ("Jupiter shield")** | Popularly said to protect inner planets from impacts. Simulations give mixed results; Jupiter may also *raise* some impactor fluxes (Horner & Jones). | Term A | Contested | **Reject as a positive factor for now. Bias flag:** popular-science claim stronger than the evidence. |
| 13 | **Large moon / obliquity stabilization** | Rare Earth argument. Recent work suggests obliquity chaos may be less fatal than claimed. | Planet-level | Contested | **Document as below model resolution.** |
| 14 | **Planet-level properties** (mass, magnetic field, plate tectonics, water inventory) | Decisive for habitability but unobservable for nearly all systems. | Absorbed into `p_hab|planet` | Gap | **Document as below model resolution.** |
| 15 | **Post-main-sequence and white-dwarf habitability** | WD HZs exist but are transient and close-in. | `TERM-T` extension | Contested | **Add later** (narrative interest). |
| 16 | **Early-universe exotic events** (pair-instability SNe, Pop III) | Relevant only in the first ~1 Gyr. | Term B, early epochs | Approximate | **Add later** if the time slider reaches that far back. |
| 17 | **Rogue planets** | Internal heat could maintain subsurface oceans. Not tied to any star's position. | Outside the per-system definition | Contested | **Document as scope limit.** |
| 18 | **Panspermia** | Would couple cells: one region could seed another. | Would break per-cell independence | Speculative | **Reject.** Too speculative, and it violates the model's locality assumption. Fine as fiction. |
| 19 | **FRBs, cosmic strings, vacuum decay, dark-matter interactions** | — | — | Speculative / negligible | **Reject**, logged as considered. Dark matter stays a placeholder per the standing bias flag. |
