# SCHEMAS — Document & Data Standards Registry

> **The single source of truth for document creation.** Any artifact type that is created **more than once** in this project must have exactly one governing schema, and that schema must be listed here. Before creating a document of a recognized type, consult its governing schema; before inventing a *new* repeatable type, register its schema here. This registry is what prevents drift, duplication, and inconsistent structure across a growing project.

---

## 1. The rule

- **Created once** (e.g. the README, the charter) → no schema needed; it is what it is.
- **Created more than once** (research documents, entity definitions, data-source descriptions, equations, factors, decisions) → **must** have a governing schema registered below, and every instance **must** conform to it.
- A change to a schema is a change to every instance's contract; record it in `DECISIONS.md` and `CHANGELOG.md`.

## 2. Registered document/data types

| Type (created repeatedly) | Governing schema | Instances / location | Notes |
|---|---|---|---|
| **Research document** | `research-document-reqs.md` | the research library | Seven-section template; cited; certainty stated |
| **Field definition** | `schema-field-definition.md` | within `entity.md`, source field maps, factor inputs | The atomic unit; owns the confidence scale & provenance tiers |
| **Data-source description** | `data-source-info-schema.md` | one per source in `data-sources-catalog.md` | Source metadata + per-field confidence map |
| **Data store** | `data-store-schema.md` | the layered stores (staging / entities / field_provenance / veil_field / spatial_index) | How ingested/processed data is laid out (ADR-012) |
| **Entity definition** | `entity.md` (fields governed by `schema-field-definition.md`) | the entity schema | *What* fields exist; *how* they're described comes from the field schema |
| **Equation** | `equations-core.md` / `equations-provisional.md` structure | the two certainty-tiered sets | Location = certainty classification (ADR-011) |
| **Factor** | `factors.md` registry format | the factor registry | Sign, regime, equations, profiles, weight, status |
| **Entity-effect wiring** | `entity-effects-matrix.md` format | the matrix | Emitter/Sampler/Receiver/Field-source; matched pair with `factors.md` |
| **Decision record (ADR)** | `DECISIONS.md` entry format | the decision log | Decision / Rationale / Rules out |
| **Changelog entry** | Keep-a-Changelog style | `CHANGELOG.md` | Added / Changed / Pending |

## 3. Shared vocabulary (defined once, referenced everywhere)

To keep the project consistent, these definitions live in exactly one place and are referenced, never re-defined:

| Concept | Canonical definition lives in |
|---|---|
| Confidence scale [0,1] & fail-safe default | `schema-field-definition.md` §4 |
| Provenance tiers (Measured/Inferred/Statistical/Modeled/Speculative) | `schema-field-definition.md` §3 |
| Blue→purple→red color mapping | `schema-field-definition.md` §5 |
| Certainty ratings (Fundamental…Missing) | `equations-provisional.md` header / `equations.md` index |
| Confidence propagation (`EQ-CORE-4`) | `equations-provisional.md` |
| Constants & parameters (values, uncertainties) | `factors.md` Appendix A |
| Roles (Emitter/Sampler/Receiver/Field-source) | `entity-effects-matrix.md` §1 |

## 4. Adding a new repeatable type
1. Write its schema as a standalone document.
2. Register it in the table above.
3. If it introduces shared vocabulary, add that vocabulary to §3 with a single canonical home.
4. Record the addition in `DECISIONS.md` (if structural) and `CHANGELOG.md`.

*This registry is itself the schema for schemas: the one place to look before creating anything the project will create again.*
