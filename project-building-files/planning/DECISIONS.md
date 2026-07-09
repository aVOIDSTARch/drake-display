# Decision Log — The Drake Display

A running record of significant decisions and their rationale, in the spirit of Architecture Decision Records (ADRs). Each entry states the decision, why it was made, and what it rules out. Entries are append-only; if a decision is reversed, a new entry supersedes the old one (and says so). This preserves the *reasoning*, not just the outcome — so future contributors can tell a deliberate choice from an accident.

---

## ADR-001 — Project name: "The Drake Display"

**Decision:** The project is named The Drake Display; "the veil" refers specifically to the rendered probability surface.
**Rationale:** Names the intellectual lineage — a hazard-aware, space-and-time-resolved extension of the Drake equation — with a crisp, memorable cadence. "Veil" describes the visual; "Display" the instrument.
**Rules out:** Prior working title "The Galactic Habitability Veil" as the project name (retained only as the descriptive surface term). A disambiguating clause ("extension of the Drake equation") is threaded through public-facing text to avoid a Drake-the-musician misread.

### ADR-002 — Log-odds factor model (not linear height summation)

**Decision:** Factors combine additively in log-odds space; the result is passed through a logistic to yield a probability.
**Rationale:** Linear addition/subtraction of heights overflows the [0,1] range at overlaps and makes compounding ill-defined. Log-odds makes independent factors compound multiplicatively in odds — the statistically principled fusion — and always yields a valid probability.
**Rules out:** Naive additive heightfields.

## ADR-003 — Galactocentric coordinate frame (not raw catalog Cartesian)

**Decision:** All entities are transformed (via astropy) from RA/Dec/distance into a galactocentric Cartesian frame.
**Rationale:** Every radius-dependent factor (metallicity gradient, density) is defined about the galactic center; heliocentric equatorial coordinates (e.g., HYG's raw x/y/z) are in a different frame and would silently corrupt the field.
**Rules out:** Reusing catalog-native Cartesian columns directly.

## ADR-004 — Dual-regime scale handling

**Decision:** Hazards are represented as smooth statistical density fields at galactic scale, and as individual point sources only in local-zoom views.
**Rationale:** A supernova's ~10 pc kill radius is sub-pixel on a 30-kpc-wide grid; individual point hazards are invisible galaxy-wide and would demand an absurd grid resolution. Two regimes reflect the real physics (statistical at large scale, discrete locally).
**Rules out:** Rendering individual point hazards on the full-galaxy grid.

## ADR-005 — Python + Plotly for Phase 0 (defer web/WebGL to Phase 1)

**Decision:** The proof-of-concept is built in Python (NumPy/SciPy/pandas/astropy) with Plotly for interactivity.
**Rationale:** The project's risk is in the model and data plumbing, not graphics; Python offers the fastest path to a validated field. Plotly delivers rotate/zoom/hover/slider from Python without a JS build. The browser/WebGL stack is the right Phase 1 target, once the model is proven.
**Rules out:** Starting in JavaScript/Three.js before the model is validated.

## ADR-006 — Specify fully before implementing

**Decision:** The model, entity schema, equation set, and build plan are written before engine code.
**Rationale:** The model's correctness (log-odds, coordinate frames, scale regimes, provenance) is subtle; specifying first prevents baking in errors and makes the build a transcription rather than a discovery.
**Rules out:** Code-first prototyping of the core model.

## ADR-007 — Provenance and certainty as first-class

**Decision:** Every equation carries a certainty rating; every entity carries speculative/provenance flags; the render shades observed vs. modeled regions differently.
**Rationale:** Most of the galaxy's data is inferred or synthetic. Distinguishing knowledge from extrapolation is what makes the tool an instrument rather than a decorative lie — and it is the project's defining principle.
**Rules out:** Presenting modeled or speculative values indistinguishably from measured ones.

## ADR-008 — Consume science-ready catalogs; do not re-reduce raw data

**Decision:** The pipeline joins existing Level-3 catalogs (Gaia parameters, APOGEE/GALAH abundances, etc.) rather than deriving parameters from raw pixels.
**Rationale:** Turning raw spectra/images into reliable stellar parameters is exactly what the large collaborations already do, with calibration an individual can't match. DIY effort is reserved for cross-matching, published relations, and population synthesis.
**Rules out:** Re-deriving parallaxes/abundances from raw survey data.

## ADR-009 — Model the Milky Way, render from any angle

**Decision:** The subject is our own galaxy, visualized in software from any viewpoint (including face-on), rather than substituting an external face-on galaxy.
**Rationale:** Per-entity 3D data (distance, motion, spectrum, planets) exists only for the Milky Way, because we're inside it. External galaxies lack per-star depth and planets. Since the visualization is software, the viewing angle is free — the external-galaxy "advantage" is moot.
**Rules out:** Building the primary model on an external galaxy for the sake of a top-down view.

## ADR-010 — Dual licensing with reserved creative fiction

**Decision:** Source code is licensed **MIT** (`LICENSE`); documentation and research content is licensed **CC BY 4.0** (`LICENSE-CONTENT`); creative/narrative fiction and the novel manuscript are **All Rights Reserved by the author**; third-party data and libraries retain their own terms; nothing outside the repository (devices, private drafts) is licensed. Each license carries an explicit scope section stating exactly what it does and does not cover.
**Rationale:** The project holds three distinct kinds of content that want three different regimes — permissive reuse for code, open-knowledge sharing with attribution for research, and full authorial control for the story. A single license would misfit at least two of them. Scoping each license to committed repository content only prevents any accidental claim over personal or unpublished material.
**Rules out:** Applying one blanket license to everything; placing the creative fiction under Creative Commons; any implication that the licenses reach files on the author's devices or third-party data.
**Open item:** the copyright-holder name in `LICENSE` and the attribution name in `LICENSE-CONTENT` are placeholders to be filled with the author's chosen legal name or handle.
