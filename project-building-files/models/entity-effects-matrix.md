# Entity-Effects Matrix — The Drake Display

> The entity-first view of the model's wiring: for each kind of entity, which effects it **emits**, **samples**, or **receives**, and in what role. This is the transpose of `factors.md` (which is factor-first) — same bipartite wiring, read from the opposite end. It is what the instantiation loop consults: when the pipeline loads an object, this document tells it *what that object does to the field*. Every factor here must exist in `factors.md`; every entity kind here must exist in `entity.md`. Section 4 checks that both directions are complete.

---

## 1. The four roles

An entity relates to the field in one or more of these roles. Most non-trivial entities hold more than one.

- **Emitter (E)** — actively *produces* an effect field (a supernova progenitor emits a hazard; an FGK star emits a favorable stellar-property field at its location).
- **Sampler (S)** — *informs* a field with its own data without producing it (a star with a measured `[Fe/H]` constrains the metallicity ridge; it reports metallicity, it doesn't beam it).
- **Receiver (R)** — the effect is *read out on it* (a terrestrial planet's habitability is simply the veil's value at its location; it emits nothing).
- **Field-source (F)** — a special role held only by the **galactic model substrate** (below): the origin of the smooth, statistical, galactic-scale factors that are not tied to any individual entity.

A single entity can be all at once. A red dwarf **emits** a flare hazard, **samples** metallicity and longevity, and — through its planets — anchors a **receiver** context.

**The two sourcing paths** (from ADR-004): factors are either **entity-sourced** (point hazards, stellar-property fields, samplers) or **field-sourced** (the smooth galactic factors, held by the substrate). The metallicity factor bridges both: field-sourced by default (modeled gradient, `EQ-CHEM-1`), locally refined wherever real stellar samplers supply measured `[Fe/H]`.

---

## 2. The matrix

| Entity kind (`entity.md`) | Roles | Emits | Samples | Receives | Lifecycle / notes |
|---|---|---|---|---|---|
| **galactic model substrate** *(pseudo-entity)* | F | `FAC-METAL` (baseline), `FAC-DENSITY`, `FAC-AGN`, `FAC-SPIRAL`, `FAC-EPOCH-GRB` | — | — | Source of all Galactic-smooth + Global-temporal factors; not an individual object |
| `star_main_sequence` (FGK) | E, S, R-ctx | `FAC-FGK`, `FAC-LONGEVITY` | `FAC-METAL`, `FAC-RADIOHEAT`, `FAC-BINARY` | via planets | The favorable baseline star; anchors habitability where it sits |
| `star_main_sequence` (M dwarf) | E, S, R-ctx | `FAC-FLARE`, `FAC-LONGEVITY` (large) | `FAC-METAL` | via planets | Same kind, low mass: longevity bonus but flare penalty — the red-dwarf fork |
| `star_giant` / `star_supergiant` | E, S | `FAC-SN` (if massive) | `FAC-METAL` | — | Evolved; supergiants are core-collapse progenitors |
| `star_wolf_rayet` | E, S | `FAC-SN`, `FAC-GRB` | `FAC-METAL` | — | Stripped, low-metallicity → prime collapsar/GRB candidate |
| `star_massive_progenitor` | E, S | `FAC-SN` (+`FAC-GRB` if collapsar) | `FAC-METAL` | — | **The marquee time-evolving hazard** (dip deepens toward collapse) |
| `brown_dwarf` | S | — | `FAC-METAL` (weak) | — | Negligible habitability driver |
| `white_dwarf` | E (minor), S | `FAC-SN` (Type Ia, if accreting binary) | `FAC-METAL` | — | Mostly inert; Type Ia channel only in interacting binaries |
| `neutron_star` / `pulsar` | E | `FAC-NSFLARE` (minor) | — | — | Point radiation hazard, short range |
| `magnetar` | E | `FAC-NSFLARE` (strong) | — | — | Strongest of the NS flare hazards |
| `black_hole` | E (conditional) | contributes to `FAC-AGN` if central/accreting | — | — | Isolated stellar-mass BH: negligible; central SMBH feeds `FAC-AGN` |
| `planet_terrestrial` / `planet_super_earth` | R, S | — | `FAC-PLANET-HZ` (own HZ status) | **habitability read out here** | The venue; where the veil's answer is evaluated |
| `planet_mini_neptune` / `planet_gas_giant` | R-ctx, S | — | `FAC-BINARY`-like (orbital perturbation) | — | Not habitable; affects system dynamics |
| `exoplanet_candidate` | R, S | — | `FAC-PLANET-HZ` | habitability (speculative) | As planet, with `is_speculative=true` |
| `planetary_system` | R-ctx | `FAC-PLANET-HZ` (system-level) | — | context aggregate | Groups a host + planets |
| `open_cluster` | E, S | `FAC-DENSITY` (local) | `FAC-METAL` (young, metal-rich) | — | Local crowding + young population |
| `globular_cluster` | E, S | `FAC-DENSITY` (extreme) | `FAC-METAL` (old, metal-poor) | — | Crowded *and* metal-poor → doubly unfavorable |
| `supernova_remnant` | E, S | `FAC-SN` (decay tail), resets `FAC-RECOVERY` | enriches ISM (→ metallicity) | — | Marker of a *past* sterilizing event |
| `hazard_collapsar` | E, S | `FAC-GRB`, `FAC-SN` | `FAC-METAL` | — | Explicit collapsar hazard object |
| `hazard_grb_candidate` | E | `FAC-GRB` (beamed) | — | — | Flagged GRB source |
| `dark_star_candidate` | S (exotic) | — | — (speculative) | — | Curiosity; high speculative flag; not a standard driver |
| `region_marker` | F-local | field factors for its region (e.g. `FAC-AGN`, `FAC-DENSITY`) | — | — | Aggregate/statistical annotation |

---

## 3. Per-kind detail (the multi-role cases)

- **M dwarf** (`star_main_sequence`, low mass) — the sharpest multi-role entity and a worked example of the red-dwarf fork. As **emitter** it produces a flare hazard (`FAC-FLARE`, declining with age) *and* an outsized longevity bonus (`FAC-LONGEVITY` — trillions of years of stability). As **sampler** it reports metallicity. Through its (often close-in) planets it anchors a **receiver** context. The net veil height at an M dwarf is a genuine tug-of-war the model must resolve, not a foregone conclusion — exactly the scientific tension from `research-stellar-energy-and-life.md`.
- **Massive progenitor / Wolf-Rayet** — the engine of the 4D demo. **Emits** `FAC-SN` (all such stars) and `FAC-GRB` (the low-metallicity, rapidly-rotating subset), both driven by `G-RAMP-SPIKE-DECAY` off the `EQ-STAR-1` clock. **Samples** its own low metallicity, which is *why* it's a GRB candidate — a nice internal consistency: the same `[Fe/H]` that lowers the metallicity ridge locally also flags the collapsar channel.
- **Terrestrial planet** — the purest **receiver**: it emits nothing; its habitability *is* the veil value at its location. It is also a **sampler** of its own habitable-zone status, which feeds `FAC-PLANET-HZ` as a positive at the host. This dual role is why planets both read from and write to the field.
- **Globular cluster** — instructive because it's **doubly unfavorable**: it emits an extreme density hazard (`FAC-DENSITY`) *and* samples low metallicity (old population), so both its emitted and sampled effects push habitability down. A clean case where roles reinforce rather than oppose.
- **Supernova remnant** — a **temporal marker**: it emits the fading tail of a past `FAC-SN` event and resets the `FAC-RECOVERY` clock for its neighborhood, while its expansion enriches the surrounding ISM (a slow positive input to metallicity). It encodes history into the present field.

---

## 4. Consistency check (both directions complete)

**Every factor has at least one source** (inverse index):

| Factor | Sourced by |
|---|---|
| `FAC-METAL` | substrate (baseline) + all stellar samplers |
| `FAC-FGK` | FGK main-sequence stars |
| `FAC-LONGEVITY` | all main-sequence stars (largest for M dwarfs) |
| `FAC-PLANET-HZ` | terrestrial planets, planetary systems |
| `FAC-RADIOHEAT` | stars (via Th/U proxy) — *placeholder* |
| `FAC-RECOVERY` | reset by supernova remnants — *construct* |
| `FAC-SN` | massive progenitors, supergiants, Wolf-Rayets, white dwarfs (Ia), SNRs (tail) |
| `FAC-GRB` | Wolf-Rayets, collapsars, GRB candidates |
| `FAC-DENSITY` | substrate + clusters (open, globular) |
| `FAC-AGN` | substrate + central black hole / region markers |
| `FAC-SPIRAL` | substrate — *contested* |
| `FAC-NSFLARE` | neutron stars, pulsars, magnetars |
| `FAC-BINARY` | multiple-star systems, gas giants |
| `FAC-FLARE` | active/M-dwarf stars — *placeholder* |
| `FAC-EPOCH-GRB` | substrate (global-temporal) — *placeholder* |
| `FAC-MOLCLOUD` | molecular clouds — *construct* |
| `FAC-KILONOVA` | neutron-star merger events |

**Every entity's declared effects map to a defined factor** — confirmed by construction: no entity in §2 emits, samples, or receives anything not present in `factors.md`. Any future addition to either document must be reflected in the other, or this check fails.

**Maintenance rule:** `factors.md` and this matrix are a matched pair. A change to one requires the corresponding change to the other in the same commit, and the §4 check must still hold.
