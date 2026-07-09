# Factors — Specification for The Drake Display

> The canonical definition of every factor that deforms the veil: what it reads, which equations it invokes, its exact spatial and temporal profiles, its sign, magnitude, backing weight, and status. This is the contract `factors.py` implements. Pairs with `entity-effects-matrix.md` (the entity-first view of the same wiring), and depends on `entity.md` (inputs), `equations.md` (math), and `spec-galactic-habitability-veil.md` (the model). Appendix A is the constants table; Appendix B is the observable→equation→certainty derivation map.

---

## 1. How a factor becomes a veil height

Each factor contributes an additive term to the log-odds of habitability (`EQ-CORE-3`):

`ℓᵢ = signᵢ · wᵢ · Mᵢ · fᵢ(space) · gᵢ(t)`

and all terms are summed and passed through the logistic (`EQ-CORE-1/2`) to yield the probability the veil displays. Therefore every factor must define six things: **sign** (±), **backing weight w** (0–1, its science-confidence), **magnitude M** (tunable strength), a **spatial profile f** (from the shared library, §3), a **temporal profile g** (§3), and a **regime** (how it is realized — see below). `w` is the honesty dial: contested factors get low `w`, not omission.

**Regimes** (from ADR-004, the dual-regime decision):

- **Galactic-smooth** — a continuous field over the disk, evaluated on the coarse grid; sourced from the structural/statistical model, not individual entities.
- **Local-point** — a discrete source with a small effect radius; visible only in local-zoom views; usually time-evolving.
- **Stellar-property** — applies at an individual star's own location, driven by its properties.
- **Global-temporal** — approximately uniform in space, varying with cosmic time.

---

## 2. Canonical factor registry

Sign: **+** raises, **−** lowers, **∩** optimum band. `w` and `M` are starting values to tune. Status: **Specified** (ready), **Placeholder** (runs on a Missing/Partial equation), **Contested** (real but low-confidence).

| ID | Name | Sign | Regime | Equations | Entity inputs | f | g | M | w | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `FAC-METAL` | Metallicity optimum band | ∩ | Galactic-smooth | EQ-CHEM-1,2,3 | `r_gal_kpc`,`feh` | P-RADIAL | G-ENRICH | 1.0 | 0.9 | Placeholder (EQ-CHEM-3/4) |
| `FAC-FGK` | FGK sweet-spot star | + | Stellar-property | EQ-STAR-2,3,4 | `teff_k`,`spectral_type` | P-STELLAR | G-STATIC | 0.8 | 0.7 | Specified |
| `FAC-LONGEVITY` | Stellar-longevity bonus | + | Stellar-property | EQ-STAR-1 | `mass_msun` | P-STELLAR | G-STATIC | 0.6 | 0.7 | Specified |
| `FAC-PLANET-HZ` | Terrestrial planet in HZ | + | Local-point | EQ-HZ-1,2,3 | planet fields, `parent_star_id` | P-STELLAR | G-STATIC | 1.0 | 0.9 | Specified (where known) |
| `FAC-RADIOHEAT` | Radiogenic-heat / tectonics | + | Stellar-property | EQ-CHEM-5 | `abundance_th_u_proxy`,`feh` | P-STELLAR | G-STATIC | 0.4 | 0.3 | Placeholder (EQ-CHEM-5) |
| `FAC-RECOVERY` | Time since last sterilization | + | Local-point | — (construct) | derived event history | P-POINT | G-RECOVERY | 0.4 | 0.3 | Construct |
| `FAC-SN` | Core-collapse SN progenitor | − | Local-point | EQ-STAR-1, EQ-HAZ-1 | `mass_msun`,`t_birth_myr` | P-POINT | G-RAMP-SPIKE-DECAY | 1.0 | 0.9 | Specified |
| `FAC-GRB` | Long-GRB / collapsar progenitor | − | Local-point (beamed) | EQ-HAZ-2,3,5, EQ-STAR-1 | `mass_msun`,`feh`,`t_birth_myr` | P-BEAMED | G-RAMP-SPIKE-DECAY | 1.2 | 0.7 | Placeholder (EQ-HAZ-3) |
| `FAC-DENSITY` | Stellar-density hazard | − | Galactic-smooth | EQ-PROF-1 | `r_gal_kpc`,`z_gal_kpc` | P-DISKDENS | G-STATIC | 0.7 | 0.6 | Specified |
| `FAC-AGN` | Galactic-center / AGN penalty | − | Galactic-smooth | — (Partial) | `r_gal_kpc` | P-INNER | G-STATIC | 0.8 | 0.5 | Placeholder |
| `FAC-SPIRAL` | Spiral-arm location | − | Galactic-smooth | — (Partial) | `x_gal_kpc`,`y_gal_kpc` | P-ARM | G-STATIC | 0.4 | 0.3 | Contested |
| `FAC-NSFLARE` | Nearby neutron star / magnetar | − | Local-point | EQ-HAZ-1 | position, `kind` | P-POINT | G-STATIC | 0.4 | 0.3 | Specified |
| `FAC-BINARY` | Close binary / multiplicity | − | Stellar-property | — (construct) | multiplicity flag | P-STELLAR | G-STATIC | 0.4 | 0.3 | Construct |
| `FAC-FLARE` | Host-star flare activity | − | Stellar-property | — (Partial) | `activity_level`,`log_lx_lbol` | P-STELLAR | G-FLARE-DECLINE | 0.5 | 0.4 | Placeholder |
| `FAC-EPOCH-GRB` | Early-universe GRB saturation | − | Global-temporal | EQ-CHEM-4, EQ-HAZ-3 | (cosmic time) | P-GLOBAL | G-ENRICH-INV | 0.6 | 0.3 | Placeholder (EQ-CHEM-4) |
| `FAC-MOLCLOUD` | Molecular-cloud passage | − | Local-point | — (construct) | cloud catalog | P-POINT | G-TRANSIENT | 0.3 | 0.2 | Construct |
| `FAC-KILONOVA` | Kilonova / short-GRB | − | Local-point | EQ-HAZ-2 | NS-merger event | P-POINT | G-SPIKE-DECAY | 0.2 | 0.2 | Specified (minor) |

---

## 3. Shared profile library

Reusable spatial (`P-`) and temporal (`G-`) functions, defined once and referenced by the registry. This keeps profiles consistent and makes `factors.py` a set of small composable functions.

**Spatial:**

- **P-RADIAL** — smooth function of galactocentric radius `R`. For `FAC-METAL`: compute `feh(R)` via `EQ-CHEM-1`, then map to influence via the optimum-band curve (`EQ-CHEM-3`, placeholder: rises from ~0 at low `[Fe/H]` to ~1 near solar, gentle decline above).
- **P-DISKDENS** — normalized double-exponential density `EQ-PROF-1`: `exp(−(R−R₀)/h_R)·exp(−|z|/h_z)`.
- **P-INNER** — steep penalty switching on inside `R_inner` (~2–3 kpc); e.g. logistic step in `R`.
- **P-ARM** — proximity to modeled spiral-arm loci (from the BeSSeL structural model).
- **P-POINT** — truncated inverse-square around a source, `EQ-PROF-2`: `min(1, r_k²/(d²+ε))`, hard cutoff at ~5·r_k.
- **P-BEAMED** — `P-POINT × f_beam`, where `f_beam = Ω_jet/4π` (`EQ-HAZ-5`); only targets within the jet cone are affected.
- **P-STELLAR** — evaluated at the star's own grid cell; influence derived from the star's properties (temperature band, mass, activity), not distance.
- **P-GLOBAL** — spatially uniform across the disk.

**Temporal:**

- **G-STATIC** — constant (= 1) over the scenario window.
- **G-RAMP-SPIKE-DECAY** — the hazard clock: ramp toward `t_collapse` (`EQ-PROF-3`), spike at collapse, exponential decay after (`EQ-PROF-4`). `t_collapse` from `EQ-STAR-1`.
- **G-SPIKE-DECAY** — one-shot spike then decay (no ramp; for merger/kilonova events).
- **G-ENRICH** — rises with cosmic time as metallicity builds (needs `EQ-CHEM-4`; **placeholder** — hold constant in Phase 0).
- **G-ENRICH-INV** — falls with cosmic time (early-universe hazards fading); inverse of G-ENRICH; same placeholder dependency.
- **G-FLARE-DECLINE** — declines as a star ages (young stars flare more).
- **G-RECOVERY** — grows since the last local sterilizing event; resets to 0 at each event.
- **G-TRANSIENT** — nonzero only during a bounded passage window.

---

## 4. Per-factor notes (only what the table can't hold)

- **`FAC-METAL`** — the project's keystone positive factor and the physical basis of the habitable annulus. Currently a Placeholder because the optimum-band mapping (`EQ-CHEM-3`) and the cosmic-time evolution (`EQ-CHEM-4`) are unresolved; Phase 0 uses a hand-tuned band, `G-ENRICH`→constant. High `w` reflects strong confidence that metallicity *matters*, even though the exact curve is pending.
- **`FAC-SN`** — the marquee time-evolving factor for the local-zoom demo. Its dip deepens over the progenitor's main-sequence life, spikes at collapse, then fades as a remnant. Fully specified; drives the Phase 0 4D demonstration.
- **`FAC-GRB`** — like `FAC-SN` but beamed and longer-reach. Lower `w` than `FAC-SN` because the rate/beaming (`EQ-HAZ-3`) is only Partial and beaming makes any single event probabilistic.
- **`FAC-METAL` / `FAC-DENSITY` interplay** — these two, opposed across galactocentric radius (metallicity favors inward, density hazard penalizes inward), are what *carve the habitable annulus*. Getting their relative `M` right is the single most important tuning task; the acceptance test (Sun in a favorable band) validates it.
- **`FAC-EPOCH-GRB`** — the temporal expression of the metallicity "double key": the early, metal-poor universe was GRB-saturated. Placeholder pending `EQ-CHEM-4`; when active, it makes the whole veil rise over cosmic time.
- **Contested/Construct factors** (`FAC-SPIRAL`, `FAC-BINARY`, `FAC-RECOVERY`, `FAC-MOLCLOUD`) carry deliberately low `w` — present for completeness, weighted to near-negligible until evidence warrants more.

---

## Appendix A — Constants & parameters

Canonical values with uncertainty and certainty tier. Values are starting points sourced from the literature; treat uncertainties as real. *(Certainty tiers per `equations.md`.)*

| Symbol | Meaning | Value | Uncertainty / range | Certainty | Used by |
| --- | --- | --- | --- | --- | --- |
| `R₀` | Sun's galactocentric radius | 8.2 kpc | ±0.1 kpc | Established | coords, P-RADIAL, P-DISKDENS |
| `z₀` | Sun's height above plane | 0.02 kpc | ±0.005 | Established | coords |
| `∇[Fe/H]` | Radial metallicity gradient | −0.06 dex/kpc | −0.05 to −0.07 | Established | EQ-CHEM-1 |
| `[Fe/H]₀` | Metallicity at `R₀` | 0.0 dex | ±0.1 | Established (by construction) | EQ-CHEM-1 |
| `h_R` | Disk radial scale length | 2.5 kpc | 2.0–3.0 | Established | EQ-PROF-1 |
| `h_z` | Thin-disk scale height | 0.3 kpc | thick disk ~0.9 | Established | EQ-PROF-1 |
| `R_inner` | Inner-region penalty onset | 2.5 kpc | 2–3 | Approximate | P-INNER |
| `r_k,SN` | Supernova kill radius | 0.010 kpc (10 pc) | 8–50 pc | Approximate | EQ-HAZ-1, P-POINT |
| `Φ_lethal` | GRB lethal fluence | 100 J/m² | — | Established | EQ-HAZ-2 |
| `r_k,GRB` | GRB extinction reach | ~1.5 kpc | 1–2 kpc (typical) | Approximate | EQ-HAZ-2, P-BEAMED |
| `θ_jet` | GRB jet half-angle | ~5° | 2–10° | Approximate | EQ-HAZ-5, P-BEAMED |
| `t_MS,☉` | MS-lifetime normalization | 1.0×10⁴ Myr | — | Approximate | EQ-STAR-1 |
| `α_MS` | MS-lifetime mass exponent | −2.5 | −2.5 to −4 | Approximate | EQ-STAR-1 |
| `S_inner` | HZ inner flux bound | 1.1 S⊕ | 1.0–1.5 | Established | EQ-HZ-2 |
| `S_outer` | HZ outer flux bound | 0.35 S⊕ | 0.32–0.53 | Established | EQ-HZ-2 |
| `b_Wien` | Wien constant | 2.898×10⁻³ m·K | exact | Fundamental | EQ-STAR-3 |
| `E_oxy` | Oxygenic photon-energy limit | 1.8 eV (~700 nm) | — | Established | EQ-STAR-4 |

---

## Appendix B — Derivation map (observable → equation → certainty tier)

For each derived quantity: what observable feeds it, through which equation, and which **honesty tier** the result lands in. This is the guard against treating an *inferred* mass or a *statistical* collapse time as if it were measured fact.

**Tier definitions:** **Direct** (computed from observables, solid) · **Inferred** (model-dependent estimate, real scatter) · **Statistical-only** (a distribution, never a deterministic value) · **Gap** (no bridging equation exists yet).

| Derived quantity | From observable(s) | Via | Tier | Caveat |
| --- | --- | --- | --- | --- |
| Luminosity | apparent mag + parallax + extinction | EQ-GEO-1, dust map | **Direct** | extinction error dominates |
| Radius | luminosity + temperature | EQ-STAR-2 | **Direct** | — |
| HZ boundaries | luminosity | EQ-HZ-2 | **Direct** | atmosphere-model dependent |
| Insolation / T_eq | luminosity + orbit | EQ-HZ-1,3 | **Direct** | albedo assumed |
| Spectral peak / photon energy | temperature | EQ-STAR-3,4 | **Direct** | — |
| Stellar mass | luminosity / isochrone / seismology | mass–luminosity, models | **Inferred** | main-sequence only; scatter; degeneracies |
| Stellar age | HR-diagram position / seismology | isochrones | **Inferred** | 30–50% error for lone dwarfs |
| Metallicity (unmeasured stars) | galactocentric radius | EQ-CHEM-1 | **Inferred** | modeled gradient, real scatter |
| Hazard collapse *timing* | mass → MS lifetime | EQ-STAR-1 | **Statistical-only** | progenitor identifiable; *date* is a distribution, not a value |
| SN / GRB *rate* per volume | stellar density, SFR, metallicity | EQ-HAZ-3, EQ-PROF-1 | **Statistical-only** | semi-empirical, large uncertainty |
| Metallicity→habitability curve | metallicity | EQ-CHEM-3 | **Gap** | giant-planet law known; full curve not |
| Metallicity vs cosmic time | — | EQ-CHEM-4 | **Gap** | needed for an honest time slider |
| Radiogenic heat → tectonics | Th/U abundance | EQ-CHEM-5 | **Gap** | no bridging equation |
| Photosynthetic availability | stellar SED | EQ-ENERGY-1 | **Gap** | exergy bounds only |

**Implementation rule:** any quantity in the **Statistical-only** or **Gap** tiers must be represented in the model with its uncertainty visible (a probability distribution, a low backing weight, or a speculative flag) — never rendered as a hard, confident value.
