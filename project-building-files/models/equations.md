# Equations — Index (Split by Certainty Tier)

> **This file has been split into two structurally-identical sets so that a document's *location* declares its trustworthiness (ADR-011).** The pipeline reads the source file to know whether an equation is load-bearing or provisional — no per-entry flag to forget, no uncertain equation sitting unmarked beside a certain one.

- **`equations-core.md`** — the **load-bearing set**: only **Fundamental** and **Established** equations. Results derived solely from these may be treated as high-confidence.
- **`equations-provisional.md`** — the **provisional set**: **Approximate / Construct / Partial / Missing**. Any result depending on these carries reduced confidence, surfaced as red/purple shading via `EQ-CORE-4`.

The confidence scale, provenance tiers, and blue→purple→red color mapping are defined once in `schema-field-definition.md`. Constants are in `factors.md` Appendix A. The document registry is `SCHEMAS.md`.
