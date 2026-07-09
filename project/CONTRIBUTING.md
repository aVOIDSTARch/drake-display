# Contributing to The Drake Display

Thank you for considering a contribution. This project spans three tracks, and you can contribute to any of them. What unites them is a single standard: **intellectual honesty is a feature.** Below is how to help, and the standards that keep the model trustworthy.

## The three tracks

- **🔭 Science** — improving the research library: adding source-cited documents, correcting the physics, sharpening coefficients, filling the named gaps in `equations.md`.
- **🧮 Model** — the model-definition layer: proposing or refining factors, spatial/temporal profiles, and the weights that drive the veil.
- **🛠️ Build** — the engine: data pipelines, coordinate math, field computation, visualization, performance.

## The honesty standards (non-negotiable)

These apply to every track and are the heart of the project:

1. **Rate certainty.** New equations carry a certainty label (Fundamental / Established / Approximate / Construct / Partial / Missing — see `equations.md`).
2. **Flag speculation.** Anything modeled, inferred, or invented is marked as such (`is_speculative`, provenance fields, or an explicit note). Never present a guess as a measurement.
3. **Name gaps.** If the equation or data doesn't exist yet, say so and add it to the gap list — don't paper over it.
4. **Cite sources.** Scientific claims reference the literature. Fabricated attributions are the one unforgivable error.
5. **Extrapolate freely, but label the deviation.** Speculative worldbuilding is welcome; disguising it as established fact is not.

## Research document standard

Every research document follows the seven-section template (see `research-document-reqs.md`): the question, established science, ongoing research, hard constraints, fertile ground for extrapolation, open questions, and brainstorm notes. Claims are cited; certainty is stated plainly; opposing views are represented fairly.

## Proposing a factor or coefficient

Factors are the heart of the model. To propose or change one:

1. State the **direction** (raises/lowers habitability) and **mechanism**.
2. Identify the **entity fields** it reads and the **equation(s)** it invokes.
3. Give its **spatial profile** `f(d)`, **temporal profile** `g(t)`, **magnitude**, and — critically — a **science-backing weight** with justification.
4. Cite the research that supports it, or flag it as a Construct/placeholder.
5. Open it as a Discussion or issue so its weight can be debated before it lands.

**Disputes about coefficients are resolved by adjusting the backing weight, not by winning an argument.** Uncertainty is represented in the model, not suppressed.

## Code standards (for the build track)

- **Language:** Python 3.11+ for Phase 0 (see `plan-phase0-veil-prototype.md` for the full stack and rationale).
- **Structure:** respect the module boundaries (ingest / coords / factors / field / render). The field model is the single source of truth; renderers only visualize it.
- **Vectorize** field math over the grid; no per-cell Python loops.
- **Reproducibility:** pin dependencies; document how to run.
- **Provenance in code:** carry `is_speculative` / backing weights through the pipeline so the render can shade honestly.

## Workflow

- **Discussions** — for open questions, science debates, factor proposals, and worldbuilding.
- **Issues** — for concrete, actionable tasks and bugs.
- **Pull requests** — reference the issue/discussion they address; explain the *why*, not just the *what*; update the relevant model-definition or research document alongside code.

## Where to start

- New to the project? Read `PROJECT_CHARTER.md`, then the `README.md`, then `roadmap-veil-project.md`.
- Want a concrete first task? The gap lists in `equations.md` and the open items in `TODO.md` are the standing to-do list.
- Not sure where you fit? Introduce yourself in Discussions and say which of the three tracks calls to you.
