# Changelog — The Drake Display

All notable changes to this project are recorded here. Format loosely follows *Keep a Changelog*; the project follows [Semantic Versioning](https://semver.org/) (ADR-015). `v0.1.0` is the first release: a working Phase 0 that passes its acceptance tests.

## [Unreleased] — Design phase

### Added — Phase 0 engine

- **Fields library (`src/fields/`):** kernels × distance metrics → spatial profiles; `SourceField` / `CompositeField`; time profiles (static, ramp–spike–decay with the EQ-STAR-1 clock); `Factor` (sign × backing × magnitude × f × g); `LogOddsField`, producing habitability H and the EQ-CORE-4 confidence channel in one pass; galactic and local grids; TOML configs with FATAL/CORRECTABLE validation; matplotlib static rendering.
- **Phase 0 pipeline (`src/veil/`, `python src/main.py`):** fetches HYG v4.1 and the NASA Exoplanet Archive with recorded retrieval dates; transforms to galactocentric coordinates with the Sun pinned at R₀ = 8.2 kpc; ingests ~120k entities; builds one supernova factor per curated massive star; writes a self-contained interactive Plotly page with entity hover and a time slider.
- **Graded per-field provenance (ADR-011):** every physical value carries `F__tier` / `F__conf` from its source field map, defaulting to Speculative/0.10; `entity.md` updated and `is_speculative` marked superseded.
- **Calibration (ADR-013):** baseline and magnitudes fitted to explicit targets, with a reproducible fit script and tests.
- **Hazard geometry (ADR-014):** true 3D slice by default; `--project-hazards` opt-in projection.
- **Tests:** 121, including the Phase 0 §6.11 acceptance checks and the calibration targets.

### Fixed

- Config validation overwrote every factor's `distance.angle_rad` with 0.0.
- The local view auto-played on load, opening part-way through time.

### Added — Design

- **Project identity:** named "The Drake Display"; README and Discussions intro authored.
- **Research library:** documents on cosmology mysteries, physics mysteries, the Drake equation, the Fermi paradox, the Kardashev scale, DNA & bio-information limits, a stellar compendium, stellar energy & life, galactic hazard distribution, and galactic chemical evolution — each following the seven-section research template with cited sources.
- **Model concept & spec:** the habitability "veil" as a log-odds probability field; factor model with science-backing weights; dual-regime (galactic-scale vs. local) hazard handling (`spec-galactic-habitability-veil.md`).
- **Model-definition layer:** entity schema (`entity.md`) and equation set with certainty ratings and explicit gap list (`equations.md`).
- **Build plans:** self-contained Phase 0 specification (`plan-phase0-veil-prototype.md`) and high-level phased roadmap (`roadmap-veil-project.md`).
- **Data infrastructure:** comprehensive public data-source catalog (`data-sources-catalog.md`).
- **Project management:** charter, governance, contributing guide, code of conduct, decision log, this changelog, security policy, and glossary.
- **Licensing:** dual-license scheme adopted (ADR-010) — MIT for source code (`LICENSE`), CC BY 4.0 for documentation/research content (`LICENSE-CONTENT`), with creative fiction reserved (All Rights Reserved) and explicit scope limiting coverage to committed repository content only.

### Pending (see `TODO.md`)

- Versioning scheme and first-release definition; issue/PR templates.
- Resolution of the Missing/Partial equations catalogued in `equations.md`.

---

*The first tagged release will correspond to a working Phase 0 prototype meeting the acceptance criteria in `plan-phase0-veil-prototype.md`.*
