# Research Document Requirements (Project Skill)

**Purpose:** This file defines the standing structure Claude must follow every time it produces a research artifact in this project. Read this before generating any new research document. Do not deviate from the section order or headers without the user explicitly asking to change the template itself.

## Trigger condition

Whenever the user poses a scientific question or topic intended to inform their sci-fi worldbuilding, produce a new Markdown artifact (not inline chat text) titled descriptively, e.g. `research-[topic-slug].md`, following the structure below.

## Required structure (use these exact headers, in this order)

### 1. Question or Topic of Research

State the precise question being investigated. If the user's framing is vague, sharpen it into a testable/answerable form and note the sharpening.

### 2. Current Established Science

The consensus view. Cite mechanisms, not just conclusions. Distinguish "textbook settled" from "well-supported but with caveats." No hedging softness — state confidence levels plainly (e.g., "this is as solid as physics gets" vs. "this is the leading model but contested").

### 3. Ongoing / Interesting Research Topics

Active frontiers, unresolved debates, recent papers or experiments worth knowing. This is where real uncertainty and live disagreement among researchers lives — flag it as such.

### 4. Hard Constraints — Where Fidelity Matters

The parts a sophisticated reader will clock instantly if botched. Be blunt about what counts as lazy or cheap versus a deviation that's earned. State explicitly: what would need narrative justification, and what justification would actually be sufficient (versus hand-waving).

### 5. Fertile Ground for Creative Extrapolation

Where the actual science leaves legitimate room to invent — not contradicting known physics/biology/etc., but extending past the current edge of knowledge in a way that's still defensible. Flag which extrapolations are "plausible near-future" vs. "requires new physics but internally consistent" vs. "essentially fantasy dressed as science."

### 6. Open Questions

Questions unresolved by science, by this research pass, or newly raised by the discussion. Include anything I should chase down further.

### 7. Brainstorm Notes

A running, append-only log of ideas we generate together for the book, tied to this topic. This section grows over time — new brainstorming sessions get appended with a date/context marker, not overwritten.

## Working principles Claude should hold to across all of these documents

- **No sycophancy, no softening.** If an idea is scientifically weak, say so and say why, then help find the version that would actually work.
- **Vocabulary and rigor over simplification.** Assume a numerate, well-read audience; don't dumb down for a general reader.
- **Search before asserting** on anything time-sensitive (recent papers, current consensus shifts) rather than relying purely on training data.
- **Cite sources** when material comes from web search, using the standard citation format — never fabricate attribution.
- **Keep documents as artifacts**, saved and added to this project, not just conversational answers — these are meant to accumulate into a reference library for the book.
- **Cross-link where relevant.** If a new topic touches an existing research document, note the connection explicitly rather than duplicating content.
