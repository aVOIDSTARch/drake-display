# Decision Log — The Drake Display

A running record of significant decisions and their rationale, in the spirit of Architecture Decision Records (ADRs). Each entry states the decision, why it was made, and what it rules out. Entries are append-only; if a decision is reversed, a new entry supersedes the old one (and says so). This preserves the *reasoning*, not just the outcome — so future contributors can tell a deliberate choice from an accident.

---

## ADR-001 — Project name: "The Drake Display"

**Decision:** The project is named The Drake Display; "the veil" refers specifically to the rendered probability surface.
**Rationale:** Names the intellectual lineage — a hazard-aware, space-and-time-resolved extension of the Drake equation — with a crisp, memorable cadence. "Veil" describes the visual; "Display" the instrument.
**Rules out:** Prior working title "The Galactic Habitability Veil" as the project name (retained only as the descriptive surface term). A disambiguating clause ("extension of the Drake equation") is threaded through public-facing text to avoid a Drake-the-musician misread.

## ADR-002 — Log-odds factor model (not linear height summation)

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

## ADR-011 — Certainty architecture: structural classification, graded per-field confidence, propagated to color

**Decision:** Trustworthiness is enforced structurally, at the level where uncertainty actually lives:

- **Equations** are split into two structurally-identical sets by certainty — `equations-core.md` (Fundamental + Established) and `equations-provisional.md` (Approximate / Construct / Partial / Missing). A document's *location* declares its status; the pipeline needs no per-entry flag.
- **Data** uses one shared schema (consumers unchanged), but every physical field value carries a mandatory `(provenance_tier, confidence)` pair with a **fail-safe default of Speculative (0.10)** — uncertainty is the default; certainty must be stated. The `is_speculative` boolean in `entity.md` is superseded by this graded per-field confidence.
- **Confidence propagates** via the now-defined `EQ-CORE-4` (weakest-link input confidence × science-backing weight, magnitude-weighted across factors) into a per-location `confidence_here`, rendered on a canonical **blue(1.0)→purple(0.5)→red(0.0)** hue scale independent of veil height.
**Rationale:** The user identified the real hazard — not storing uncertain data near certain data, but any default that *reads as certain*. Two parallel data stores were rejected for bulk data because uncertainty is **per-field, not per-record** (a star's position is measured while its age is inferred and its metallicity modeled, in one row); splitting entities across stores would scatter records and force per-field merging on consumers. The two-store pattern *is* adopted for equations, which are discrete and each hold one stable rating. Making confidence a mandatory structural pair with an uncertain default achieves fail-safe classification at the correct granularity. The color scheme is the render of propagated confidence — which is what justified finally specifying `EQ-CORE-4`.
**Rules out:** Two parallel *data* catalogs; boolean-only speculation flags; any value entering the pipeline without a confidence; treating absent confidence as certain.
**Enacted by:** `schema-field-definition.md`, `data-source-info-schema.md`, `equations-core.md`, `equations-provisional.md`, `equations.md` (index), `SCHEMAS.md`.

## ADR-012 — Layered data storage: by source, then by entity, then by space-time

**Decision:** Processed/ingested data is organized in three layers, each with its own organizing principle:

- **Ingest** — organized **by source** (`staging/{source}`), preserving original columns and per-source field confidences; the provenance-of-record and re-processing origin.
- **Canonical** — organized **by entity** (`entities`), one record per resolved object, where each field is a **cell** carrying value + source + provenance_tier + confidence (highest-confidence value surfaced), with a long-format `field_provenance` audit ledger retaining all source values.
- **Derived** — organized **by space-time** (`veil_field`, arrays) and a **spatial index** for entity picking. The computed veil field `H(x,y,z,t)` and `confidence_here` are stored as chunked arrays, *not* as entity rows.
**Rationale:** Data arrives by source but is consumed by entity, and confidence is per-field/per-source (ADR-011). A single "by source" processed store would force consumers to join across sources at read time (rejected); a single "by entity" store without provenance would lose the per-source confidence. Layering keeps the canonical store entity-oriented (consumers unchanged) while retaining full source provenance upstream and downstream. The veil field is a scalar field over a grid, not entity data, so it is stored in its natural array shape — the dual-regime (ADR-004) reappearing at the storage layer.
**Rules out:** A single flat store; storing the computed field inside entity rows; discarding non-surfaced source values; entity-oriented storage that drops per-field provenance.
**Enacted by:** `data-store-schema.md`.

## ADR-013 — Phase 0 calibration targets

**Decision:** The Phase 0 baseline and factor magnitudes are fitted to explicit targets rather than left at the `factors.md` starting values. Targets, at z = 0:

- H ≈ 0.20 at the galactic center, ≈ 0.75 at the solar radius (R = 8.2 kpc, the peak), ≈ 0.40 at R = 20 kpc.
- H rises monotonically from the center to the solar radius.
- A core-collapse supernova at collapse drives H to ≤ 0.10 inside its kill radius, against the solar background.

Fit, with signs, backings and profiles unchanged and the `FAC-DENSITY : FAC-AGN` magnitude ratio held at the `factors.md` 0.7 : 0.8: baseline −0.51; `FAC-METAL` M = 1.83; `FAC-DENSITY` M = 1.75; `FAC-AGN` M = 2.0; `FAC-SN` M = 3.7. Resulting H across the disk (R = 0, 2, 4, 6, 8.2, 12, 20 kpc): 0.20, 0.39, 0.69, 0.73, 0.75, 0.67, 0.40.
**Rationale:** The starting values gave a veil that barely moved (H 0.46–0.71 galaxy-wide; a supernova at collapse only reached 0.50), which made the instrument unable to show the contrasts the model exists to show. Explicit targets make the tuning reviewable and testable. The density : core ratio is fixed because an unconstrained four-target fit needed a *negative* core magnitude and produced a non-monotonic disk — fitting noise, not physics. The targets are judgments about legibility, not measurements: a different reasonable target set would be equally defensible, which is why they are written down.
**Caveat:** The solar peak remains partly built in: the placeholder metallicity band (`EQ-CHEM-3`) peaks at solar metallicity, which falls at the solar radius by construction. Resolving `EQ-CHEM-3` will require recalibrating.
**Rules out:** Untuned starting values in rendered output; magnitudes changed without updating the targets and tests.
**Enacted by:** `configs/phase0-galactic.toml`, `src/veil/registry.py` (`SN_MAGNITUDE`), `scripts/calibrate_phase0.py`, `tests/test_calibration.py`.

## ADR-014 — Local-view hazard geometry: true 3D slice by default, projection opt-in

**Decision:** The local-zoom veil is evaluated on the Sun's plane, and point hazards reach it by **true 3D distance** by default, so a star more than about one cutoff radius (~50 pc for a supernova) above or below the plane leaves no dip there. A `--project-hazards` option instead measures hazard distance **in the plane only** (from the star's vertical axis), so every nearby star's dip is shown. The page says which geometry it is using.
**Rationale:** About half of the real nearby massive stars sit more than 50 pc off the Sun's plane, so the honest slice shows only some of them dipping, which reads as missing data. Projection shows them all, but overstates the reach of off-plane stars — a 100 pc-off star would appear to sterilize the plane directly beneath it. Neither is wrong as a view; only the slice is a faithful evaluation of the model at the plane, so it is the default, and the projection is available and labelled when the goal is to see where hazards are.
**Rules out:** Silently projecting hazards; a projected view without an on-page statement that reach is overstated.
**Enacted by:** `src/veil/registry.py` (`supernova_factor(..., project_onto_plane)`), `src/veil/main.py` (`--project-hazards`), `src/veil/interactive.py` (`intro_html`).

## ADR-015 — Semantic versioning; v0.1.0 is Phase 0

**Decision:** The project follows Semantic Versioning (MAJOR.MINOR.PATCH). The first release, `v0.1.0`, is defined as a working Phase 0 that passes its acceptance tests (`plan-phase0-veil-prototype.md` §9, `tests/test_phase0_acceptance.py`). While the major version is 0, the public interfaces (config schema, entity table columns, CLI) may still change between minor versions.
**Rationale:** Date-based entries suited the design phase, when nothing executable existed. Now that there is an engine with configs and a data schema others could depend on, version numbers should signal compatibility. Tying `v0.1.0` to the acceptance tests makes the first release an objective bar rather than a judgment call.
**Rules out:** Date-based version labels for the engine; a first release that does not pass the Phase 0 acceptance tests.
**Enacted by:** `docs/project/CHANGELOG.md`, `pyproject.toml` (`version`).

## ADR-016 — Short slug: `drake-display`

**Decision:** The project's short name, for repositories, package names and other identifiers where "The Drake Display" won't fit, is `drake-display`.
**Rationale:** It matches the existing GitHub repository name, keeps the full name recognisable, and drops the article, which slugs conventionally omit.
**Rules out:** Other slugs for the same project (e.g. the internal library name `fields` as the distribution name).
**Enacted by:** `pyproject.toml` (`name`), the GitHub repository `aVOIDSTARch/drake-display`.

## ADR-017 — Attribution and credit policy

**Decision:** Contributions are credited where they belong, by kind:

- **`AUTHORS.md`** (`docs/project/`) lists contributors grouped by track — Science, Model, Build, Worldbuilding — each with a one-line note. Listing is opt-in, under the name or handle the contributor chooses.
- **Code** is credited by the git history, with `Co-authored-by` trailers for paired work.
- **Scientific contributions** (coefficients, corrections, sources) are also credited inline in the document or `factors.md` entry that uses them.
- **`CITATION.cff`** at the repository root gives the citation metadata (MIT and CC-BY-4.0), kept in step with `AUTHORS.md` by the maintainer.
- **Worldbuilding** contributions are credited in the repository; credit within the All-Rights-Reserved fiction (ADR-010) is at the author's discretion and is not promised.
- **AI-assisted work** is disclosed, for code via a `Co-Authored-By` trailer.

**Rationale:** The project's three tracks produce different kinds of work, and one list can't credit them all well: commits already record code precisely, while a science contribution is only meaningful next to the number it changed — the same reason every value carries its own confidence. Opt-in naming respects contributors who don't want a legal name in a public repository. Separating repository credit from credit in the fiction keeps the creative work's rights clear and avoids a promise the license doesn't make. Disclosing AI assistance follows from the honesty standard: provenance applies to authorship too.
**Rules out:** Listing people without consent; a single undifferentiated contributor list; implied credit in the published fiction; undisclosed AI-drafted work.
**Enacted by:** `docs/project/AUTHORS.md`, `CITATION.cff`, `CONTRIBUTING.md` (Credit), `GOVERNANCE.md`, `LICENSE-CONTENT`.
