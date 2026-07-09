# Project Charter — The Drake Display

> The foundational reference: what this project is, what it is not, what "done" means, and the principles that govern every decision. When any later document or conversation drifts, this is the document that settles it.

## Vision

A model of the Milky Way that shows **where and when life is plausible** — habitability rendered as a probability field with a geography and a history, grounded in real data where it exists and honest speculation where it does not, with the boundary between the two always visible.

## Mission

Extend the Drake equation from a single number into a spatially- and temporally-resolved, hazard-aware instrument: an interactive 4D map (the "veil") backed by a rigorous, source-cited research library that supplies and justifies its every coefficient.

## Scope

**In scope**

- A computational model of galactic habitability as a log-odds probability field over 3D space and cosmic time.
- An interactive visualization (rotate, zoom, click entities, scrub time).
- A research library establishing the science behind each factor and coefficient.
- A formal model-definition layer (entity schema, equation set, factor/effect definitions) and a phased build plan.
- Honest provenance: measured vs. inferred vs. modeled vs. speculative, always distinguished.

**Out of scope (for now)**

- Galaxies other than the Milky Way (the MW is uniquely rich in per-entity data; external galaxies are a possible far-future extension).
- Real-time observational feeds or original data collection (the project consumes published catalogs).
- Deriving new stellar parameters from raw pixels (we join existing science-ready catalogs).
- A finished novel (the fiction is the *motivation*, developed separately; this project is its instrument).

## Goals & objectives

1. Prove the field model works (Phase 0).
2. Deliver an interactive 3D, then 4D, galaxy (Phases 1–2).
3. Ground it in real survey data with visible provenance (Phase 3).
4. Make it tunable and shareable (Phase 4).
5. Grow a research library whose rigor a knowledgeable reader trusts.

## Non-goals

- Not a game or a general-purpose planetarium.
- Not a claim to predict actual alien life — it models *plausibility*, with stated uncertainty.
- Not a monolith: each phase stands alone and delivers value independently.

## Success criteria

- **Phase 0:** the veil renders as a valid probability field; the Sun lands in a favorable band; a hazard dip deepens over a time slider. *(See `plan-phase0-veil-prototype.md` for exact acceptance tests.)*
- **Overall:** a running instrument in which every displayed height traces to an equation and a data source, every speculative region is visibly flagged, and the coefficients are defensible from the research library.

## Audience & stakeholders

- **Primary:** the project author, as a worldbuilding instrument for hard science fiction.
- **Secondary:** contributors across three communities — astrophysics, data visualization/engineering, and hard-SF worldbuilding.
- **Tertiary:** the curious public who want to see the habitable galaxy across space and time.

## Guiding principles

1. **Honesty over comfort.** Rate certainty; flag speculation; name gaps. A visible "we don't know" beats a confident guess.
2. **Research and tool are one loop.** Every coefficient traces to a document; every model gap directs new research.
3. **Phase independence.** Each phase is a usable artifact on its own.
4. **Rigor as courtesy to the reader.** The point of the discipline is that a knowledgeable audience can trust the ground.
5. **Specify before building.** Design the model, schema, and equations before writing engine code.

## Constraints & assumptions

- Most of the galaxy's per-entity data is inferred or synthetic; fidelity is inherently non-uniform (sharp locally, fuzzy elsewhere). This is displayed, not hidden.
- Coefficients begin as tunable, clearly-labeled modeling choices and graduate to defensible values as research matures.
- The project is built incrementally by a small team (initially one), so scope discipline is essential.

## Key deliverables (compiled to date)

- Research library (cosmology, physics, DNA/bio-information, stellar compendium, stellar energy & life, galactic hazards, galactic chemical evolution).
- Model-definition layer (`entity.md`, `equations.md`; `factors.md` and the entity-effects matrix pending).
- Build documents (`plan-phase0-veil-prototype.md`, `roadmap-veil-project.md`).
- Data source catalog (`data-sources-catalog.md`).
- Project management set (this charter, governance, contributing, code of conduct, decision log, changelog, security, glossary).
