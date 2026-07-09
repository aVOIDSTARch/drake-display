# The Galactic Habitability Veil

**A four-dimensional model of galactic habitability — mapping where, and *when*, the Milky Way could hold life.**

---

Imagine a translucent veil draped across the disk of the galaxy. Where conditions favor life, it rises; where a hazard lurks — a massive star spiraling toward collapse, the crowded violence of the core, the metal-starved outer dark — it dips. Overlapping influences compound. And then you reach for a slider marked *time*, and the whole surface begins to move: the habitable galaxy forming, shifting, and reshaping itself across billions of years as heavy elements spread outward and the early universe's gamma-ray storms subside.

That is what this project builds. Not an artist's impression — a **model**, grounded in real astronomical data where it exists, honest speculation where it doesn't, and a clear, visible line between the two.

## What this is

The Veil has two intertwined tracks, and neither works without the other:

- **A modeling engine** — an interactive, rotatable, zoomable 3D map of the Milky Way with a fourth axis, time. Each entity (star, planet, remnant, hazard) is a clickable object; the "veil" is a computed probability field describing habitability at every point, deforming as factors compound and as the clock runs.
- **A research library** — a growing collection of rigorous, source-cited science documents (stellar physics, galactic chemical evolution, the gamma-ray-burst and supernova hazard census, the bioenergetics of starlight, and more) that supply and justify every coefficient the model uses. The research calibrates the tool; the tool exposes which research still needs doing. One loop, not two projects.

## The core idea

Habitability is not uniform, and it is not eternal. It has a **geography** and a **history**. This project treats that literally:

- A **log-odds factor model** combines many positive and negative influences into a single valid probability field — so effects compound the way independent evidence should, without ever breaking the bounds of probability.
- Each factor carries not just a magnitude but a **science-backing weight**, so the map encodes *how much we trust each height*, not merely the height itself.
- A **time dimension** lets the model evolve: stars ignite, age, and die; enrichment spreads; hazards flare and fade. The habitable galaxy is something you watch happen.

## What makes it different

**Intellectual honesty is a first-class feature, not an afterthought.**

- Every equation is rated by certainty — from *Fundamental* physical law down to *Construct* (an explicit modeling choice) and *Missing* (a gap we refuse to paper over).
- The map is designed to **shade observed regions differently from modeled and speculative ones**. Most of the galaxy's data is inferred or synthetic — because we sit inside the disk, behind dust, unable to photograph our own galaxy from outside — and the Veil shows you exactly where knowledge ends and extrapolation begins. That distinction is the difference between an instrument and a pretty lie.
- Gaps are named, not hidden. The project maintains explicit lists of the equations and parameters we *don't yet have*, each tied to the research that would supply it.

## The science it stands on

Real data, real physics, real uncertainty:

- **Astrometry & catalogs** — Gaia (1.8 billion stars now; the DR4 exoplanet and binary release lands December 2026), plus ready-made 3D star catalogs, spectroscopic metallicity surveys, and hazard registries.
- **Real equations on observable inputs** — luminosity and habitable zones from magnitude, parallax, and temperature; a stellar-lifetime clock for hazard timing; a metallicity gradient across the disk; supernova and gamma-ray-burst lethality from the peer-reviewed literature.
- **Honest limits** — some quantities (a lone star's mass and age, a supernova's exact collapse date) are *inferred* or *statistical*, never measured. The model treats them accordingly rather than pretending otherwise.

## Project structure

The repository is organized as layers that build on one another:

- **Research library** — the science documents that justify the model.
- **Model-definition layer** — the formal specification: the entity schema (`entity.md`), the equation set with certainty ratings (`equations.md`), and the factor and effects definitions that bind data to math.
- **Build plans** — a detailed, self-contained Phase 0 specification and a high-level phased roadmap for the whole arc.
- **The engine** — the code, arriving phase by phase.

## Status & roadmap

The project is in active design, **fully specified ahead of implementation** — the model, data schema, equation set, and build plan exist before the first line of engine code, by intent.

- **Phase 0 — Prove the model.** Python proof-of-concept: the field math, the coordinate pipeline, and a first time-evolving hazard. *(Specified; ready to build.)*
- **Phase 1 — Interactive 3D.** A real rotatable, zoomable, clickable browser application.
- **Phase 2 — The fourth dimension.** A fully populated galaxy you can scrub through time.
- **Phase 3 — Real data & honest provenance.** Survey data at scale, with observed-vs-modeled shading.
- **Phase 4 — Polish & share.** Live tuning, deep entity views, saveable scenarios.

Each phase is independently valuable. You can stop at any boundary and still hold something worth having.

## Getting involved

This project sits at the intersection of astrophysics, data visualization, and hard-science-fiction worldbuilding — and it welcomes people from all three. Whether you want to argue about a coefficient, contribute a factor, sharpen a piece of the science, or help build the engine, there's a place for you. Start a conversation in **Discussions**, or open an issue.

## Why it exists

Beneath the astrophysics, this is a worldbuilding instrument. It was born to give a work of science fiction a galaxy whose habitable geography is *non-arbitrary* — where civilizations, migrations, and catastrophes sit where the physics actually supports them, and where a knowledgeable reader finds ground solid enough to trust. The ambition outgrew the story. What began as research for a novel became a model of the living galaxy in its own right.

---

*The Veil maps a galaxy that is only now, after thirteen billion years, becoming truly habitable — and whose best age for life may lie in the deep future. Come help chart it.*
