# Changelog — The Drake Display

All notable changes to this project are recorded here. Format loosely follows *Keep a Changelog*; the project uses date-based entries during the pre-release design phase and will adopt semantic versioning once the engine ships.

## [Unreleased] — Design phase

### Added

- **Project identity:** named "The Drake Display"; README and Discussions intro authored.
- **Research library:** documents on cosmology mysteries, physics mysteries, the Drake equation, the Fermi paradox, the Kardashev scale, DNA & bio-information limits, a stellar compendium, stellar energy & life, galactic hazard distribution, and galactic chemical evolution — each following the seven-section research template with cited sources.
- **Model concept & spec:** the habitability "veil" as a log-odds probability field; factor model with science-backing weights; dual-regime (galactic-scale vs. local) hazard handling (`spec-galactic-habitability-veil.md`).
- **Model-definition layer:** entity schema (`entity.md`) and equation set with certainty ratings and explicit gap list (`equations.md`).
- **Build plans:** self-contained Phase 0 specification (`plan-phase0-veil-prototype.md`) and high-level phased roadmap (`roadmap-veil-project.md`).
- **Data infrastructure:** comprehensive public data-source catalog (`data-sources-catalog.md`).
- **Project management:** charter, governance, contributing guide, code of conduct, decision log, this changelog, security policy, and glossary.
- **Licensing:** dual-license scheme adopted (ADR-010) — MIT for source code (`LICENSE`), CC BY 4.0 for documentation/research content (`LICENSE-CONTENT`), with creative fiction reserved (All Rights Reserved) and explicit scope limiting coverage to committed repository content only.

### Pending (see `TODO.md`)

- Factor specification (`factors.md`) and the entity-effects matrix.
- Parameters/constants table and the observable→equation→certainty derivation map.
- Maintainer contact, versioning scheme, issue/PR templates.
- Resolution of the Missing/Partial equations catalogued in `equations.md`.

---

*The first tagged release will correspond to a working Phase 0 prototype meeting the acceptance criteria in `plan-phase0-veil-prototype.md`.*
