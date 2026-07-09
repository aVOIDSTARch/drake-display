# Roadmap: The Galactic Habitability Veil — Full Project Phasing (High-Level)

> The complete arc, kept intentionally high-level. Each phase is independently valuable — you can stop at any boundary and still have a working, useful artifact. Detailed build specs live in their own documents (e.g., `plan-phase0-veil-prototype.md`); this is the map, not the terrain. A parallel **research track** (the science documents in this project) runs alongside and feeds the model's coefficients throughout.

---

## The shape of the project in one breath
A model that computes a habitability "probability height" across the Milky Way, deformed by hazards and favorable factors, evolving over time — built up from a Python proof-of-concept, to an interactive 3D web app, to a fully populated 4D (space + time) engine grounded in real survey data, ultimately serving as both a reasoning tool and a worldbuilding instrument for the fiction.

---

## Phase 0 — Prove the model
- **Goal:** validate the core math and data pipeline; de-risk the whole project.
- **Builds:** log-odds factor field, coordinate pipeline, a galactic-scale veil surface, and one time-evolving hazard in a local zoom.
- **Stack:** Python (NumPy/SciPy/pandas/astropy) + Plotly.
- **Unlocks:** confidence that the concept works before investing in real engineering.
- **Done when:** the field renders, stays a valid probability, the Sun lands in a favorable band, and a massive star's dip deepens toward collapse on a time slider. *(Detailed spec already written.)*

## Phase 1 — Make it a real interactive 3D application
- **Goal:** move from a Python plot to a genuine rotatable/zoomable/clickable 3D tool, single epoch.
- **Builds:** browser app with real entities as clickable objects (info on click), the veil as a deformable 3D mesh, full camera control.
- **Stack shift:** rendering moves to the web (Three.js/WebGL or deck.gl); the Phase 0 field model stays the single source of truth and is only *visualized* here.
- **Unlocks:** most of the visual dream, minus time and full-galaxy coverage.
- **Done when:** a user can fly around the disk, click a star, and read its data, with the veil responding to the underlying factors.

## Phase 2 — Add the fourth dimension and populate the galaxy
- **Goal:** the marquee capability — scrub time back and forth across a fully populated galaxy.
- **Builds:** procedural population synthesis to cover the regions no telescope has resolved; per-entity temporal state functions (stars igniting, aging, dying) driving the field's evolution; smooth time scrubbing.
- **Stack additions:** population-synthesis tooling (TRILEGAL-style) at the data layer.
- **Unlocks:** the living map — watch the habitable galaxy form and shift as enrichment spreads and hazards flare and fade.
- **Done when:** dragging the time slider evolves a whole, populated disk coherently, not just a handful of hand-placed objects.

## Phase 3 — Ground it in real data and real science
- **Goal:** replace modeled placeholders with measured data and defensible coefficients.
- **Builds:** ingestion of Gaia astrometry, APOGEE/GALAH metallicity, real hazard catalogs (pulsars, SNRs, Wolf-Rayet progenitors), and dust; coefficient tuning against the research-track literature; a **provenance/confidence layer** that visually distinguishes observed regions from modeled/speculative ones.
- **Stack additions:** out-of-core dataframes (Dask/Vaex) at the ingestion boundary for survey-scale data.
- **Unlocks:** a tool that is honest about what it knows versus guesses — the difference between an instrument and a pretty lie.
- **Done when:** the veil is driven by real survey data where it exists, clearly flagged, with coefficients traceable to the science documents.

## Phase 4 — Polish, depth, and sharing
- **Goal:** turn a working engine into a usable, shareable instrument.
- **Builds:** live factor-weight tuning UI, rich entity deep-dives, scenario save/load and export, performance optimization, and ingestion of new data as it lands (e.g., Gaia DR4's exoplanet and binary catalogs, Dec 2026).
- **Unlocks:** a tool others can use, and that you can drive interactively while writing.
- **Done when:** the engine is stable, tunable, and shareable, with saved scenarios.

---

## The parallel research track (runs throughout)
The science documents in this project are not separate from the tool — they are its **coefficient source and sanity check**. Every factor weight and backing score in the veil traces back to a research document (metallicity gradients, GRB rates, supernova kill radii, stellar spectra). As the research deepens, the model sharpens; as the model surfaces questions, it directs new research. Treat them as one loop, not two projects.

## How it serves the fiction (the point of all of it)
At any phase past 0, the veil is already a worldbuilding instrument: it makes the habitable galaxy's geography *non-arbitrary*, gives regions and epochs real character, and lets you site your story's civilizations, migrations, and catastrophes where the physics actually supports them. The tool and the research exist to make the eventual fiction stand on ground that a knowledgeable reader will trust.
