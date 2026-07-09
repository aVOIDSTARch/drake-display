# Governance — The Drake Display

How decisions get made, who makes them, and how disagreements resolve. Kept deliberately lightweight for a small project, designed to scale if the community grows.

## Roles

- **Maintainer / Lead** — the project author; holds final say on scope, direction, and merges; owns the charter and roadmap. *(Currently a single person; may expand.)*
- **Science reviewers** — contributors trusted to vet the research library and coefficient proposals for scientific soundness and honest sourcing.
- **Build contributors** — those working on the engine.
- **Contributors** — anyone opening issues, discussions, or pull requests. No formal barrier to entry.

As the project grows, additional maintainers may be added by invitation of the Lead, based on sustained, high-quality contribution.

## Decision-making

- **Ordinary changes** (a new research document, a bug fix, a well-justified factor) proceed by pull request and review; the Lead or a designated reviewer merges.
- **Model-definition changes** (edits to `entity.md`, `equations.md`, factors, or the field model) require explicit review because they ripple through the whole system. They are proposed openly (Discussion/issue) before implementation.
- **Structural decisions** (architecture, stack, scope, naming) are recorded as entries in `DECISIONS.md` (the decision log) so the reasoning is preserved and revisable.

## Resolving scientific & coefficient disputes

This project has an unusual and deliberate mechanism: **the model represents uncertainty, so disputes need not be won.**

- When contributors disagree about a coefficient, the resolution is to set the **backing weight** to reflect the genuine state of evidence — a contested factor gets a low weight and a documented note, not a forced consensus.
- When the science itself is unsettled, the research document represents the competing positions fairly (per the seven-section template) rather than declaring a winner.
- The Lead breaks genuine deadlocks, but the default is to encode the disagreement honestly rather than suppress it.

## Changing the model-definition layer

Because `entity.md`, `equations.md`, and the factor definitions are the contract the whole engine depends on:

- Additions are welcome (the schema and equation set only grow).
- Removals or breaking changes require a Decision-log entry and maintainer sign-off.
- Any change that touches a coefficient must update its backing weight and cite (or flag the absence of) supporting research.

## Amending governance

This document is itself changeable by pull request with maintainer approval, recorded in the decision log.
