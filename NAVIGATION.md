# Navigating The Drake Display

This guide is for anyone opening the repository for the first time. It explains what each folder holds, where to start reading for what you care about, and where new files belong.

If you want to know what the project *is*, read the [README](README.md) first. It takes about five minutes.

---

## The layout at a glance

```text
drake-display/
├── README.md            What the project is, and how to run it
├── NAVIGATION.md        This guide
├── LICENSE              MIT, for the code
├── LICENSE-CONTENT      CC BY 4.0, for the documents and research
├── CITATION.cff         How to cite the project
├── pyproject.toml       Python package definition
├── requirements.txt     Pinned versions of the Python dependencies
│
├── docs/                Everything written for people to read
├── src/                 The engine's source code
├── tests/               Automated tests for the engine
├── configs/             Model settings: the factors and their strengths
├── data/                Input data
└── scripts/             Helper programs: calibration, demo renders
```

The split is simple. **`docs/` is for reading; everything else is the working engine.** Generated files (downloaded catalogs, rendered output) never go in either. They land in folders that git ignores, described [below](#files-you-wont-find-in-git).

---

## `docs/`: the documentation

Each subfolder answers one question.

| Folder | The question it answers | Start with |
| --- | --- | --- |
| [`docs/project/`](docs/project/) | Where is the project going, and how is it run? | [`CHARTER.md`](docs/project/CHARTER.md) |
| [`docs/research/`](docs/research/) | What does the science say? | [`research-drake-equation.md`](docs/research/research-drake-equation.md) |
| [`docs/model/`](docs/model/) | What exactly does the model compute? | [`spec-galactic-habitability-veil.md`](docs/model/spec-galactic-habitability-veil.md) |
| [`docs/data-sources/`](docs/data-sources/) | Where does the data come from, and how far can it be trusted? | [`data-sources-catalog.md`](docs/data-sources/data-sources-catalog.md) |
| [`docs/schemas/`](docs/schemas/) | How is each piece of data described? | [`SCHEMAS.md`](docs/schemas/SCHEMAS.md) |
| [`docs/engineering/`](docs/engineering/) | How is the engine built? | [`plan-phase0-veil-prototype.md`](docs/engineering/plan-phase0-veil-prototype.md) |
| [`docs/community/`](docs/community/) | How do people take part? | [`discussions-intro-v0.2.md`](docs/community/discussions-intro-v0.2.md) |
| [`docs/images/`](docs/images/) | Pictures used by other documents | — |
| [`docs/archive/`](docs/archive/) | What was superseded? | — |

Three standard files sit directly in `docs/`, where GitHub also finds them: [`CONTRIBUTING.md`](docs/CONTRIBUTING.md) (how to help, and the honesty standards), [`CODE_OF_CONDUCT.md`](docs/CODE_OF_CONDUCT.md) and [`SECURITY.md`](docs/SECURITY.md).

### `docs/project/`: running the project

| File | What it is |
| --- | --- |
| [`CHARTER.md`](docs/project/CHARTER.md) | Purpose, scope, and what the project will and won't do |
| [`ROADMAP.md`](docs/project/ROADMAP.md) | The phases, from Phase 0 (prove the model) to Phase 4 (polish and share) |
| [`DECISIONS.md`](docs/project/DECISIONS.md) | The decision log. Each numbered entry (ADR-001, ADR-002, …) records a choice, the reasoning, and what it rules out |
| [`TODO.md`](docs/project/TODO.md) | Open decisions, unfinished documents, and science gaps |
| [`CHANGELOG.md`](docs/project/CHANGELOG.md) | What changed, release by release |
| [`GOVERNANCE.md`](docs/project/GOVERNANCE.md) | Who decides what, and how disagreements are settled |
| [`AUTHORS.md`](docs/project/AUTHORS.md) | Who has contributed, by track |
| [`GLOSSARY.md`](docs/project/GLOSSARY.md) | Definitions of project terms: veil, factor, backing weight, and so on |
| [`WHODIS.md`](docs/project/WHODIS.md) | Who the maintainer is |

### `docs/research/`: the research library

Source-cited science documents, each following the seven-section template in [`research-document-reqs.md`](docs/research/research-document-reqs.md). They cover the Drake equation, the Fermi paradox, the Kardashev scale, stellar types, starlight and life, galactic chemical evolution, and the distribution of galactic hazards.

[`other-science/`](docs/research/other-science/) holds related reading that doesn't feed the model directly: cosmology mysteries, the limits of DNA as information storage, and rotating-frame forces.

### `docs/model/`: the model definition

This is the formal contract the engine implements. Read it in this order:

1. [`spec-galactic-habitability-veil.md`](docs/model/spec-galactic-habitability-veil.md): the concept. A habitability surface over the galaxy, built from factors that raise or lower it.
2. [`entity.md`](docs/model/entity.md): every kind of object (star, planet, hazard), and every field it can carry.
3. [`equations.md`](docs/model/equations.md): an index of every equation. The equations themselves are split by certainty into [`equations-core.md`](docs/model/equations-core.md) (well established) and [`equations-provisional.md`](docs/model/equations-provisional.md) (approximate, placeholder, or missing).
4. [`factors.md`](docs/model/factors.md): each factor's direction, strength, confidence, and shape in space and time.
5. [`entity-effects-matrix.md`](docs/model/entity-effects-matrix.md): the same wiring viewed from each entity's side.

[`factors-v2.md`](docs/model/factors-v2.md) is a **proposed** replacement for `factors.md`, under discussion. It isn't used by the engine yet.

### `docs/data-sources/` and `docs/schemas/`: the data and how it's described

- [`data-sources-catalog.md`](docs/data-sources/data-sources-catalog.md) surveys the public datasets the project could use.
- [`source-at-hyg.md`](docs/data-sources/source-at-hyg.md) and [`source-nasa-exoplanet-archive.md`](docs/data-sources/source-nasa-exoplanet-archive.md) describe the two catalogs the engine reads today. Each maps every column to the model, with a stated confidence.
- [`schema-field-definition.md`](docs/schemas/schema-field-definition.md) is the most important schema. It defines the five provenance tiers (Measured, Inferred, Statistical-only, Modeled, Speculative), the 0–1 confidence scale, and the blue → purple → red colors used to show confidence.
- [`SCHEMAS.md`](docs/schemas/SCHEMAS.md) indexes the rest.

### `docs/engineering/`: building the engine

| File | What it is |
| --- | --- |
| [`plan-phase0-veil-prototype.md`](docs/engineering/plan-phase0-veil-prototype.md) | The Phase 0 build spec and its definition of done. This is what the current code implements |
| [`pipeline-idea-v2.md`](docs/engineering/pipeline-idea-v2.md) | The end-to-end pipeline design, from raw catalogs to the rendered veil, across all phases |
| [`pipeline-v1-assessment.md`](docs/engineering/pipeline-v1-assessment.md) | Why the first pipeline draft (now in `archive/`) was replaced |
| [`setup-python-project.md`](docs/engineering/setup-python-project.md) | Notes on setting up the Python project |
| [`pseudocode/`](docs/engineering/pseudocode/) | Early pseudocode for two core classes |

---

## The engine

| Folder | What's in it |
| --- | --- |
| [`src/fields/`](src/fields/) | A general-purpose library for fields over space: falloff shapes, distance measures, time profiles, factors, and the field that combines them. It knows nothing about astronomy |
| [`src/veil/`](src/veil/) | The Phase 0 pipeline that applies `fields` to the galaxy: download catalogs, convert coordinates, build the entity table, assemble the factors, render |
| [`src/main.py`](src/main.py) | The single entry point: `python src/main.py` |
| [`tests/`](tests/) | Tests, including the Phase 0 acceptance checks (`test_phase0_acceptance.py`) and the calibration targets (`test_calibration.py`) |
| [`configs/`](configs/) | The model's settings as TOML files: which factors exist, their signs, strengths, and confidences |
| [`data/curated/`](data/curated/) | Small hand-made input data, such as the list of nearby massive stars |
| [`scripts/`](scripts/) | `calibrate_phase0.py` reproduces the calibrated settings; `phase0_static.py` renders the two-star demo |

How to install and run it is in the README, under [Running Phase 0](README.md#running-phase-0).

### Files you won't find in git

Running the engine creates three folders that git ignores:

- **`data/raw/`**: downloaded catalogs, fetched automatically on first run, with download dates recorded in `retrieved.json`.
- **`data/processed/`**: the combined entity table the pipeline builds.
- **`output/`**: rendered results. Open `output/phase0/veil.html` in a browser for the interactive view.

All three can be deleted at any time; the next run recreates them.

---

## Suggested reading paths

**Just curious.** Read the [README](README.md), then run the engine and open `output/phase0/veil.html`. Then look through [`docs/research/`](docs/research/) for whatever interests you.

**A scientist checking the model.** Read [`schema-field-definition.md`](docs/schemas/schema-field-definition.md) to see how certainty is graded, then [`equations-core.md`](docs/model/equations-core.md) and [`equations-provisional.md`](docs/model/equations-provisional.md), then [`factors.md`](docs/model/factors.md). Corrections are welcome; see the honesty standards in [`CONTRIBUTING.md`](docs/CONTRIBUTING.md).

**Proposing or changing a factor.** Read [`factors.md`](docs/model/factors.md), then "Proposing a factor or coefficient" in [`CONTRIBUTING.md`](docs/CONTRIBUTING.md). Then read ADR-013 in [`DECISIONS.md`](docs/project/DECISIONS.md) to see how strengths are calibrated, and [`configs/phase0-galactic.toml`](configs/phase0-galactic.toml) to see where they live.

**A developer working on the engine.** Read [`plan-phase0-veil-prototype.md`](docs/engineering/plan-phase0-veil-prototype.md), then [`src/veil/main.py`](src/veil/main.py), which wires the whole pipeline in about 120 lines. Then run `pytest`.

**Here for the worldbuilding.** Read the "Why it exists" section of the [README](README.md), then [`research-galactic-hazards-distribution.md`](docs/research/research-galactic-hazards-distribution.md) and [`research-galactic-chemical-evolution.md`](docs/research/research-galactic-chemical-evolution.md). These explain why some parts of the galaxy favor life and others don't.

**Wondering why something is the way it is.** Search [`DECISIONS.md`](docs/project/DECISIONS.md). Structural choices are recorded there along with what they rule out.

---

## Where new files go

| You're adding… | Put it in | Notes |
| --- | --- | --- |
| A research document | `docs/research/` | Follow [`research-document-reqs.md`](docs/research/research-document-reqs.md); name it `research-<topic>.md` |
| A tangential science write-up | `docs/research/other-science/` | Same template |
| A change to the model | `docs/model/` | Changes here need review first; see [`GOVERNANCE.md`](docs/project/GOVERNANCE.md) |
| A new data source | `docs/data-sources/` | Use the format in [`data-source-info-schema.md`](docs/schemas/data-source-info-schema.md); name it `source-<name>.md` |
| A structural decision | an entry in `docs/project/DECISIONS.md` | Use the next ADR number |
| A design or build plan | `docs/engineering/` | |
| A document that has been replaced | `docs/archive/` | Keep it; don't delete it |
| An image | `docs/images/<topic>/` | |
| Code | `src/fields/` if it's general, `src/veil/` if it's specific to the galaxy model | Add tests in `tests/` |
| Model settings | `configs/` | |
| Small hand-made data | `data/curated/` | Note where every value came from, and how much to trust it |

**Naming.** Project-level files use capitals (`ROADMAP.md`, `DECISIONS.md`). Content documents use lowercase with hyphens (`research-fermi-paradox.md`). When one document mentions another, it usually gives the bare filename in `code` style, and every filename in `docs/` is unique, so searching for the name finds the file.
