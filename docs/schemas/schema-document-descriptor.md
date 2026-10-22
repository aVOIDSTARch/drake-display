# Schema: Document Descriptor — The Drake Display

> **The document-level counterpart of `schema-field-definition.md`.** Where that schema says how to describe a single *data field*, this one says how to describe a single *document*: what it is, whether it's current, whether other work must conform to it, who it's for, and what to read first. Every document in the repository is described this way, in one manifest, [`docs/documents.toml`](../documents.toml). Governed by `SCHEMAS.md`.

---

## 1. Why this exists

The repository holds more than sixty documents. They differ in kind (research, model contracts, plans, policies), in standing (current, proposed, replaced), and in authority: some are binding contracts the code must follow, while others are background reading. That information used to live only in each document's opening paragraph, phrased differently each time.

The descriptor states it once, in the same shape for every document, so that a person or a tool can answer questions like these without opening each file:

- Which documents are current?
- Which ones does the code have to conform to?
- What should I read before this one?
- What replaced this?

## 2. The descriptor (required structure)

Each document is described by one `[[document]]` entry in `docs/documents.toml`:

| Attribute | Required | Meaning |
| --- | --- | --- |
| `path` | ✓ | Path from the repository root, e.g. `docs/model/factors.md`. Unique across the manifest |
| `title` | ✓ | The document's title. For a Markdown or license file that starts with a `# ` heading, it must match that heading exactly |
| `type` | ✓ | What kind of document it is; one of the types in §3 |
| `status` | ✓ | Whether it's current; one of the statuses in §4 |
| `normative` | ✓ | `true` if other documents or the code **must conform to it** (a contract, standard, policy, or license). `false` if it is informative: background, a proposal, a record, or a guide |
| `audience` | ✓ | Who it is mainly for: one or more of the audiences in §5 |
| `summary` | ✓ | One sentence saying what the document is for. A single line, ending with a period |
| `governed_by` | — | The schema this document is an instance of, per the `SCHEMAS.md` registry. Example: every research document is governed by `research-document-reqs.md` |
| `depends_on` | — | Documents to read first: the ones this document builds on or refers to as its basis. Each must be in the manifest |
| `supersedes` | — | The document this one replaced |
| `superseded_by` | — | What replaced this document. Required when, and only when, `status = "superseded"`. It may be a document or another file, such as the source code that implements a design sketch |
| `version` | — | The document's own version label, when it has one (e.g. `"v0.2"`) |

A descriptor with an unknown attribute, or one missing a required attribute, is invalid.

## 3. Document types (canonical)

| Type | Meaning | Examples |
| --- | --- | --- |
| `overview` | Orientation for newcomers | `README.md`, `NAVIGATION.md` |
| `license` | Legal terms | `LICENSE`, `LICENSE-CONTENT` |
| `policy` | Rules for taking part | `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `GOVERNANCE.md` |
| `project-record` | Records and plans for running the project | `CHARTER.md`, `ROADMAP.md`, `DECISIONS.md`, `TODO.md`, `CHANGELOG.md` |
| `research` | A source-cited science document | `research-drake-equation.md` |
| `model` | Part of the model definition | `entity.md`, `factors.md`, `equations-core.md` |
| `schema` | A standard that other documents or data must follow | `schema-field-definition.md`, `research-document-reqs.md` |
| `template` | A blank form to copy | `whodis-bespoke-template.md` |
| `data-source` | A description of one data source, or the catalog of sources | `source-at-hyg.md` |
| `engineering` | A build plan, design, or engineering note | `plan-phase0-veil-prototype.md` |
| `code-guide` | Documentation of the engine's code | `code-architecture.md` |
| `community` | Material for the project's community spaces | `discussions-intro-v0.2.md` |

## 4. Statuses (canonical)

| Status | Meaning | Rules |
| --- | --- | --- |
| `draft` | Being written; not yet ready to rely on | — |
| `proposed` | Complete, but awaiting a decision before it takes effect | Must not be `normative`, since nothing has to conform to it yet |
| `active` | Current and in force | — |
| `superseded` | Replaced, and kept for the record | Requires `superseded_by`. Lives in `docs/archive/`, and every document in `docs/archive/` has this status |

## 5. Audiences (canonical)

`everyone`, `contributors`, `scientists`, `developers`, `maintainers`, `worldbuilders`.

## 6. Scope

The manifest describes every **document**:

- every `.md` and `.txt` file under `docs/`;
- the root `README.md` and `NAVIGATION.md`;
- the two license files.

It does not describe code, configs, data, images, or machine-readable metadata (`CITATION.cff`, `pyproject.toml`, the manifest itself).

## 7. Enforcement

`tests/test_document_manifest.py` checks the manifest against the repository on every test run:

- every document in scope has exactly one entry, and every entry's file exists;
- every descriptor has exactly the allowed attributes, with valid values;
- titles match the documents' headings;
- every referenced path resolves, and nothing refers to itself;
- the status rules in §4 hold.

**Adding, moving, renaming, or retiring a document therefore means updating the manifest in the same change.** The test fails until you do.

## 8. Worked example

```toml
[[document]]
path = "docs/model/factors-v2.md"
title = "Factors v2 — Specification for The Drake Display"
type = "model"
status = "proposed"
normative = false
audience = ["scientists", "contributors"]
summary = "Proposed replacement for factors.md that splits the single log-odds sum into three terms combined in log space."
depends_on = ["docs/model/factors.md", "docs/model/entity-effects-matrix.md", "docs/model/entity.md"]
version = "v2"
```

When `factors-v2.md` is accepted, it becomes `active` and `normative`, gains `supersedes = "docs/model/factors.md"`, and `factors.md` moves to `docs/archive/` with `status = "superseded"` and `superseded_by = "docs/model/factors-v2.md"`.
