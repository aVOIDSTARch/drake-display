# Spec: The Galactic Habitability "Veil" — Factor Model, Data Inventory & Feasibility Assessment

> Purpose: This is a *build document*, not a research document — it does not follow the seven-section research template. It specifies the conceptual model, an exhaustive weighted factor list, the mathematics of the "veil," an inventory of what public data actually exists (and what doesn't), and a phased, honest feasibility path toward a rotatable/zoomable 4D (3D + time) interactive model of Milky Way habitability. Draws its factors from `research-galactic-hazards-distribution.md`, `research-stellar-energy-and-life.md`, `research-galactic-chemical-evolution.md`, and `research-stellar-compendium.md`.

---

## Part A — The concept, stated precisely

You want a scalar field draped over the galactic disk: a **habitability probability height** H at every point, deformed downward by hazards (dips) and upward by favorable factors (ridges), with overlapping effects compounding, and the whole surface re-computable at any chosen cosmic time t via a slider. That is, formally:

**H(x, y, z, t)** = a scalar field over 3D space and time, rendered as a deformable surface ("veil") above the disk plane, with the underlying entities (stars, remnants, hazard sources) plotted as clickable objects at their real or modeled 3D positions.

This is a completely coherent and buildable idea. The veil is, mathematically, a **heat/height field** — the same object as a topographic surface or a heatmap — and rendering deformable height fields in 3D is a solved, standard problem. The genuine difficulty is *not* the graphics; it is (1) the coefficients (which are uncertain, hence the backing scores below) and (2) the fact that real whole-galaxy data doesn't exist the way you're picturing (Part D). Both are manageable.

---

## Part B — The mathematics of the veil

### B.1 Work in odds/log space, not raw probability

Your instinct that "overlapping effect areas would compound" is right, but *how* they compound matters. If you simply add and subtract heights linearly, strong overlapping effects can push probability below 0 or above 1, which is meaningless. The principled fix is to work in **log-odds** (the way real statistical models combine independent evidence): each factor contributes an additive term to the log-odds, which is equivalent to *multiplying* the odds — so effects compound naturally and the result always stays a valid probability after you transform back. Concretely:

**logit(H) = B₀ + Σᵢ (wᵢ · Mᵢ · fᵢ(distance) · gᵢ(t))**  then  **H = 1 / (1 + e^(−logit(H)))**

where for each factor i:

- **wᵢ** = science-backing weight (your confidence the factor is real; see the table's 1–5 score, normalized to 0–1)
- **Mᵢ** = effect magnitude coefficient (how strongly it pushes habitability, signed: + raises, − lowers)
- **fᵢ(distance)** = spatial falloff profile (how the effect fades with distance from its source)
- **gᵢ(t)** = temporal profile (how the effect turns on/off/deepens as the time slider moves)

For a remedial first version you can drop the logistic wrapper and just clamp a linear sum to [0,1] — but adopt the log-odds form as soon as you're compounding more than a few factors, or the map will lie to you at the overlaps.

### B.2 The two profile shapes you'll reuse constantly

- **Spatial falloff f(d):** for point hazards (a supernova, a nearby magnetar) use an inverse-square-like or Gaussian falloff truncated at a hard "kill/effect radius" beyond which f = 0 (e.g., ~10 pc for a supernova, ~1–2 kpc for a beamed GRB — see the hazards document for real numbers). For broad fields (metallicity, stellar density) use a smooth gradient across the disk.
- **Temporal profile g(t):** this is what makes it 4D and is your marquee feature. Your own example — a massive star that carves a *deepening dip* as it approaches core collapse, then detonates, then fades — is exactly a g(t) that ramps up over the star's main-sequence lifetime, spikes at its death, and decays as the remnant cools. Each entity gets a state function of t derived from stellar-evolution timescales (main-sequence lifetime ≈ 10 Gyr × (M/M☉)^−2.5 is a serviceable first approximation).

---

## Part C — The exhaustive factor list

Direction: **+** raises habitability, **−** lowers it, **∩** optimum band (bad at both extremes). Backing score: 1 (speculative) → 5 (robust). Coefficient is a *suggested relative starting weight* to tune, not a measured constant — the whole point of the backing score is to keep you honest that these are model choices.

| # | Factor | Dir | Mechanism | Spatial character | Temporal character | Backing (1–5) | Suggested coeff (rel.) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | **Metallicity — planet floor** | + | Enough heavy elements to form rocky planets & life-chemistry | Higher toward center; declines ~0.06 dex/kpc outward | Rises over cosmic time (enrichment) | 5 | +1.0 |
| 2 | **Metallicity — excess** | − | Possible hot-Jupiter overproduction disrupting terrestrials | Innermost/most-enriched regions | Emerges late in enriched zones | 2 | −0.2 |
| → | *(1 & 2 together = an optimum band, ∩)* | ∩ | | | | | |
| 3 | **FGK "sweet-spot" star present** | + | Visible-rich spectrum ideal for oxygenic photosynthesis | Point source at each such star | Active during that star's main sequence | 4 | +0.8 |
| 4 | **Stellar longevity / stability** | + | Long stable main sequence = time for life to evolve | Favors lower-mass (K/M) stars | Spans the (long) MS lifetime | 4 | +0.6 |
| 5 | **Terrestrial planet in habitable zone** | + | The actual venue for life | Point source | Present once formed; HZ migrates as star ages | 5 (where known) | +1.0 |
| 6 | **Dynamical quiet (low perturbation)** | + | Stable orbits, undisturbed Oort cloud | Interarm, outer thin disk | Varies with arm crossings | 3 | +0.3 |
| 7 | **Radiogenic-heat budget (tectonics/dynamo)** | + | U/Th/K power plate tectonics & magnetic shield | Tracks enrichment (metallicity) | Set at planet formation | 3 | +0.4 |
| 8 | **Core-collapse SN progenitor (O/B)** | − | Ozone-stripping blast; deepens toward collapse | Kill radius ~8–50 pc | Dip deepens over MS life, spikes at death, fades | 5 | −1.0 |
| 9 | **Long-GRB / collapsar progenitor** | − | Beamed ozone-stripping burst; huge reach | ~1–2 kpc but *beamed* (probabilistic) | Ramps to collapse; one-shot | 4 | −1.2 |
| 10 | **High stellar density** | − | Compounds SN/GRB rate + dynamical disruption | Rises steeply toward center; clusters | Higher in past (denser, more SF) | 4 | −0.7 |
| 11 | **Galactic-center / AGN proximity** | − | Sgr A* outbursts, radiation, crowding | Innermost few kpc only | Episodic; worse during AGN-active phases | 3 | −0.8 |
| 12 | **Spiral-arm location** | − | Elevated SN density, molecular clouds, cosmic rays | Along arms | Cyclic as system crosses arms | 3 (contested) | −0.4 |
| 13 | **Low metallicity (planet-starved)** | − | Too few solids to build planets | Outer disk, halo | Dominant in early universe | 5 | −1.0 |
| 14 | **Nearby neutron star / magnetar** | − | Point radiation hazard (flares) | Short range (pc-scale for lethality) | Fades as remnant ages | 3 | −0.4 |
| 15 | **Close binary / multiplicity** | − | Disrupts stable habitable-zone orbits | Point source | Persistent | 3 | −0.4 |
| 16 | **Host-star flare activity** | − | Superflares strip atmospheres (esp. M dwarfs) | Point source | Worse when star is young; declines w/ age | 4 | −0.5 |
| 17 | **Epoch-wide early-universe GRB saturation** | − | Metal-poor cosmos = collapsar-rich everywhere | Global (whole disk) | Strong early, fades after ~5 Gya | 3 | −0.6 |
| 18 | **Molecular-cloud passage** | − | Radiation environment + dust + dynamical stirring | Along dense gas | Transient during passage | 2 | −0.3 |
| 19 | **Time since last local sterilization** | + | Recovery/accumulation window for complex life | Local | Resets at each hazard event, grows after | 3 | +0.4 |
| 20 | **Kilonova / short-GRB (NS merger)** | − | Minor ozone hazard, far weaker than long GRB | Short-to-moderate range | One-shot, rare | 2 | −0.2 |

Notes: factors 1/2/13 are really one metallicity axis with an optimum band — implement as a single ∩-shaped field rather than three separate terms if you prefer. Factors 8/9/16 are your best candidates for the dramatic time-slider behavior you described, because their g(t) genuinely deepens toward a discrete catastrophic moment.

---

## Part D — The honest reality check: why no "topographic map of the galaxy" exists

This shapes your entire architecture, so I'm putting it plainly rather than burying it. **There is no detailed, empirical, face-on map of the Milky Way, and there cannot easily be one, for two physical reasons:**

1. **We are inside the disk.** We can't photograph our galaxy from outside; every "face-on Milky Way" image you've seen is an *artist's impression* or a *model*, not a photograph. <cite index="56-1">The best such renderings (e.g., the Gaia-based Payne-Wardenaar image) are reconstructions incorporating data from many papers, and Gaia has even overturned basic assumptions — showing the galaxy has more than two spiral arms, less prominent than thought, and a more inclined central bar.</cite>
2. **Dust blocks the view.** The galactic plane is opaque with interstellar dust, so we cannot see through the disk to the far side in visible light at all.

What this means for you: **precise 3D data exists for the solar neighborhood and degrades with distance.** Gaia's parallax distances are superb nearby and grow uncertain across the disk. So a *whole-galaxy* map is necessarily **real data locally + a structural model globally + procedural/speculative population to fill the gaps** — which is *exactly* the "use fake/speculative info at first" approach you proposed. That instinct isn't a compromise; it's the scientifically standard method (population synthesis). You are not doing something hacky by faking the far side — everyone does, because the data physically cannot exist yet.

---

## Part E — Data inventory: what's public right now

All of the following are free and publicly accessible.

**Structural substrate (the disk itself):**

- **Gaia (ESA)** — the crown jewel. <cite index="50-1">DR3 (June 2022) contains information for over 1.8 billion sources and is public now; DR4 is expected 2 December 2026</cite>, and <cite index="48-1">DR4 will contain ~2.8 billion processed sources (~2 billion high-quality), including — for the first time — an exoplanet list, non-single-star/binary solutions, and per-source astrophysical parameters</cite>. Access via the Gaia ESA Archive (ADQL queries), or programmatically through `astroquery`. This is your precise local 3D backbone.
- **Spiral-arm / bar structural models** — the BeSSeL survey (Reid et al.) maser-parallax model gives the galaxy's arm geometry as usable parameters; ideal as the "model substrate" for the regions Gaia can't resolve.

**Ready-made 3D star catalogs (start here for a prototype):**

- **HYG database** — a merged Hipparcos + Yale + Gliese catalog of ~120,000 stars *with pre-computed Cartesian x/y/z coordinates*, distributed as plain CSV on GitHub. It is essentially purpose-built for hobbyist 3D star-map projects and is the fastest possible on-ramp for your remedial version.
- **Gaia Catalogue of Nearby Stars (GCNS)** — ~331,000 stars within 100 pc, clean and complete for the immediate neighborhood.

**Planets:**

- **NASA Exoplanet Archive** — all confirmed exoplanets (5,500+) with host-star coordinates, distances, and system parameters. Free, queryable, downloadable.

**Object registries (for the "click an entity, get info" feature):**

- **SIMBAD** (CDS Strasbourg) — cross-identifications and basic data for ~10+ million objects, with a public API.
- **VizieR** (CDS) — thousands of published catalogs behind one query interface.

**Hazard-source catalogs (to place your dips):**

- **ATNF Pulsar Catalogue** — ~3,000+ neutron stars/pulsars with positions.
- **Green's Catalogue of Galactic Supernova Remnants** — the standard SNR list.
- **Wolf-Rayet and massive-star catalogs** — your collapsar/long-GRB and core-collapse progenitor candidates (factors 8, 9).

**Chemistry (for the metallicity field, factors 1/2/13):**

- **APOGEE** (SDSS) and **GALAH** — large stellar spectroscopic surveys giving [Fe/H] and [α/Fe] across the disk; the empirical basis for your metallicity ridge.

**Dust (for realism and obscuration effects):**

- **3D dust maps** — Green et al. "Bayestar" and the high-resolution Edenhofer et al. (2024) map (out to ~1.25 kpc). Optional but adds authenticity.

**Filling the unobserved galaxy (procedural population):**

- **Galaxia / TRILEGAL** — population-synthesis tools that generate statistically realistic synthetic stellar populations for any line of sight or volume. This is how you honestly populate the far side of the disk your telescopes can't see.

**Prior-art visualizers to learn from (don't reinvent):**

- **Gaia Sky** (ESA, open source) — <cite index="52-1">an outreach application built specifically to explore the galaxy in 3D using Gaia data</cite>. Study it; it is the closest existing thing to your dream and its source is available.
- **OpenSpace** (NASA-affiliated, open source) and **Celestia** — mature 3D astronomical visualization engines with time controls.

---

## Part F — Feasibility & a phased build path

**Verdict: yes, feasible — and the remedial version is genuinely achievable by one motivated person.** The graphics are standard; the data (locally) exists; the coefficients you get to define and refine. Here is a sane escalation:

- **Phase 0 — 2.5D static prototype (days–weeks).** Python + Plotly (or matplotlib). Load the HYG CSV. Compute H on a 2D grid over the disk plane from a handful of factors (metallicity gradient + a few point hazards). Render as a heatmap/contour with a crude z-height. Prove the field math and the log-odds compounding. No time yet.
- **Phase 1 — 3D interactive, single epoch (weeks–months).** Move to WebGL — **Three.js** (maximum control) or **deck.gl**/**Plotly 3D** (faster to stand up). Plot real stars at their x/y/z as clickable points (Three.js raycasting → info panel pulling from your catalog join). Render the veil as a deformable height *mesh* above the plane. Add rotate/zoom/pan (orbit controls). This already delivers most of your dream minus time.
- **Phase 2 — the 4D time slider (months).** Give each entity a state function of t (using stellar-evolution timescales for the dramatic hazard ramps in factors 8/9/16). Add a procedural population (TRILEGAL-style) so the whole disk is covered, not just the observed neighborhood. Recompute H(t) on slider drag. This is where your "massive star deepening its dip as it nears collapse" comes alive.
- **Phase 3 — polish & realism (ongoing).** Ingest Gaia/APOGEE at scale for a real metallicity field; add dust obscuration; refine coefficients against literature; add save/share of scenarios; layer in DR4 (Dec 2026) exoplanets and binaries when released.

**Where the real effort goes (manage expectations):** not the rendering, but (a) *data plumbing* — cross-matching catalogs into one queryable store keyed by object, so a click returns unified info; (b) *the coefficient model* — every number in Part C is a defensible starting guess, not a measured truth, and tuning them so the veil "feels right" without lying is the actual intellectual work; and (c) *the temporal model* — evolving a whole population across Gyr is the ambitious part, so start with a static snapshot plus a few hand-authored evolving hazards before attempting a fully procedural time-evolving galaxy.

**One caveat to keep visible in the UI itself:** because most of the galaxy's data is modeled or synthetic (Part D), the veil should visually distinguish *observed* regions (real Gaia data, solar neighborhood) from *modeled/speculative* regions (everywhere else). Encoding data provenance/confidence into the display — perhaps as a transparency or texture overlay — keeps the tool honest and is itself a striking feature, not a limitation.

---

## Appendix — Minimal starter data set for Phase 0

If you want the shortest path to a working toy: (1) **HYG database** CSV for star positions; (2) **NASA Exoplanet Archive** CSV for known planets; (3) a hard-coded **metallicity gradient** function (−0.06 dex/kpc, rising with time) for factor 1/13; (4) a dozen hand-placed **Wolf-Rayet / O-star** positions from any massive-star catalog for factors 8/9; (5) the factor table above for coefficients. That is enough to render a first veil with a working time slider on a laptop.
