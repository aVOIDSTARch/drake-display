# TODO — The Drake Display

Open items surfaced by the project-management documents and the model-definition layer. Split into **Decisions needed** (a human must choose), **Documents/artifacts to complete**, and **Deferred / phase-gated** (deliberately not yet decided). Each item notes where it came from.

---

## Decisions needed (a human must choose)

- [x] **License(s).** ✅ Resolved (ADR-010): **MIT** for code (`LICENSE`), **CC BY 4.0** for documentation/research (`LICENSE-CONTENT`), **All Rights Reserved** for creative fiction/manuscript, third-party data under its own terms, nothing off-repo covered. **Remaining sub-task:** fill the copyright-holder / attribution name placeholders in both license files with your chosen legal name or handle.
- [ ] **Maintainer contact address.** Needed for `SECURITY.md` (vulnerability reports) and `CODE_OF_CONDUCT.md` (enforcement contact). Currently placeholdered. *(Surfaced by: SECURITY, CODE_OF_CONDUCT.)*
- [ ] **Repository hosting details.** Confirm the platform/URL and whether Discussions, Issues, and Wiki are enabled; align the intro blurb accordingly. *(Surfaced by: discussions-intro, README.)*
- [ ] **Versioning scheme & first-release definition.** Confirm semantic versioning post-engine, and that "v0.1.0" = a working Phase 0 meeting its acceptance tests. *(Surfaced by: CHANGELOG.)*
- [ ] **Project short name / handle & repo tagline.** Confirm the one-line repo description (draft: *"A hazard-aware, four-dimensional extension of the Drake equation — mapping where and when the Milky Way could hold life."*) and any short slug. *(Surfaced by: ADR-001, README.)*
- [ ] **Attribution/credits policy.** How contributors (science, code, worldbuilding) are credited. *(Surfaced by: GOVERNANCE, CONTRIBUTING.)*

## Documents / artifacts to complete

- [x] **`factors.md` — Factor Specification.** ✅ Done: canonical factor registry, shared profile library, per-factor notes, plus the constants/parameters table (Appendix A) and the observable→equation→certainty derivation map (Appendix B).
- [x] **Entity-effects matrix.** ✅ Done (`entity-effects-matrix.md`): the entity-first view with Emitter/Sampler/Receiver/Field-source roles and a two-way consistency check. Built as a matched pair with `factors.md`.
- [x] **Ingestion column crosswalk.** ✅ Done via per-source descriptions: `source-at-hyg.md` and `source-nasa-exoplanet-archive.md` (built on `data-source-info-schema.md`) — each gives the column→`entity.md` field map, per-field confidences, unit fixes, filters, and entity-resolution notes `ingest.py` needs.
- [ ] **Propagate graded confidence through `entity.md`.** Mechanical pass: replace the single `is_speculative` boolean with per-field `provenance_tier` + `confidence` per `schema-field-definition.md`, and add source field maps per `data-source-info-schema.md`. *(Surfaced by: ADR-011.)*
- [ ] **Issue & PR templates** (`.github/`). Structured templates aligned to the three tracks and the honesty standards. *(Surfaced by: CONTRIBUTING, GOVERNANCE.)*
- [ ] **Canonical `ROADMAP.md`.** Either promote `roadmap-veil-project.md` to the conventional filename or link it. *(Surfaced by: repo convention.)*
- [ ] **`CITATION`/references consolidation.** A single bibliography behind the research library's cited claims. *(Surfaced by: CONTRIBUTING honesty standards.)*

## Scientific gaps to close (from `equations.md`)

These block certain factors from graduating past placeholder. Each maps to a research-library document.
- [ ] **`EQ-CHEM-3`** — the metallicity → habitability optimum-band curve (*Partial*).
- [ ] **`EQ-CHEM-4`** — metallicity as a function of radius *and* cosmic time, `[Fe/H](R,t)` (*Missing*; needed for an honest time slider on the metallicity ridge).
- [ ] **`EQ-CHEM-5`** — radiogenic heat → tectonic/dynamo longevity → habitability (*Missing*).
- [ ] **`EQ-HAZ-1`** — a closed-form supernova lethality(distance) beyond empirical kill radii (*Partial*).
- [ ] **`EQ-HAZ-3`** — an adopted parametrization for the GRB rate field `R_GRB(R,t)` (*Partial*).
- [ ] **`EQ-ENERGY-1`** — a usable photosynthetic-energy-availability equation from stellar SED (*Partial*).
- [x] **`EQ-CORE-4`** — ✅ Defined (ADR-011): confidence propagation (weakest-link × backing weight, magnitude-weighted) → per-location `confidence_here` → blue/purple/red hue. Now a Construct in `equations-provisional.md`, no longer Missing.

## Deferred / phase-gated (deliberately not yet decided)

- [ ] **Phase 1 web stack** — Three.js vs. deck.gl vs. other. Decide at Phase 1 start, not before. *(Surfaced by: roadmap, Phase 0 handoff notes.)*
- [ ] **Out-of-core data strategy** (Dask/Vaex) — introduce only when scaling past AT-HYG to Gaia-scale data (Phase 3). *(Surfaced by: Phase 0 plan handoff.)*
- [ ] **Scenario persistence / save-load format** — Phase 4. *(Surfaced by: roadmap.)*
- [ ] **Live coefficient-tuning UI** — Phase 4. *(Surfaced by: roadmap.)*
- [ ] **External-galaxy extension** — explicitly out of scope now; revisit as a possible far-future direction. *(Surfaced by: charter, ADR-009.)*
- [ ] **Gaia DR4 ingestion** (exoplanets, binaries) — plan for after its December 2026 release. *(Surfaced by: README, data catalog.)*

---

*Maintenance note: when an item is resolved, record the resolution in `DECISIONS.md` (if it's a structural choice) and in `CHANGELOG.md`, then check it off here.*
