# Assessment: `pipeline-idea-v1.md` vs. The Drake Display's actual architecture

> Reviewed against `DECISIONS.md`, `plan-phase0-veil-prototype.md`, `roadmap-veil-project.md`, `spec-galactic-habitability-veil.md`, `equations-core.md`, `equations-provisional.md`, `factors.md`, `entity.md`, and `data-store-schema.md`. The `other-science/` and `research/` folders were excluded, per instruction, since this is a systems-architecture question, not a science-content one.

## Bottom line

**Discard this as an architecture proposal.** It solves a different, much harder problem than the one this project has, contradicts five already-ratified decisions in `DECISIONS.md`, and never once engages with the model it's supposedly a pipeline *for* — no mention of log-odds, factors, entities, provenance, or a single equation ID. It reads like a generic "how do I build a fast large-scale GPU field simulation" answer, produced without the project's own specs in view, and pasted in with heavy internal repetition (the same recommendation is restated in five different forms — "Recommended architecture," "Recommended stacks," "My recommendation," "High-level layout," then a full pseudocode skeleton — before anything project-specific appears).

Everything in this document that *is* sound (Zarr for large snapshots, out-of-core dataframes, a WebGL-family renderer) is already independently specified, better, and with project-specific rationale, in the docs already in the repo. It adds nothing; it only proposes replacing decided, appropriately-scoped choices with a distributed HPC stack the project doesn't need and one person can't reasonably maintain.

---

## 1. The core mismatch: this project has no PDE

The entire document is built around a **stateful field simulation**: a `PDE` on a grid, `finite-difference/finite-volume` update rules, per-cell `evaluate_equations(cell, neighborhood, time)`, `ghost_cells`, `exchange_boundary_data`, `active_region_index`, double-buffered timestep integration. That architecture exists to solve one specific kind of problem: **a field whose value at time `t+1` depends on its own neighbors' values at time `t`** (diffusion, fluid flow, wave propagation — problems where information has to physically propagate cell-to-cell).

The Drake Display's veil field is not that. Per `EQ-CORE-1`/`EQ-CORE-2` (`equations-core.md`) and `EQ-CORE-3` (`equations-provisional.md`):

```text
ℓᵢ = signᵢ · wᵢ · Mᵢ · fᵢ(space) · gᵢ(t)
logit(H) = B₀ + Σᵢ ℓᵢ
H = expit(logit(H))
```

Every `fᵢ(space)` and `gᵢ(t)` in `factors.md`'s 17-factor registry — `P-RADIAL`, `P-DISKDENS`, `P-INNER`, `P-ARM`, `P-POINT`, `P-BEAMED`, `P-STELLAR`, `P-GLOBAL`, and all seven `G-*` temporal profiles — is a **closed-form function of position, time, and entity properties**, evaluated independently at each grid point. There is no cell that needs to know its neighbor's value to compute its own. This is a pure **map** operation — trivially vectorized in NumPy today, and embarrassingly parallel on a GPU if it's ever needed — not a simulation requiring time-integration, stencils, or boundary exchange between compute chunks. `plan-phase0-veil-prototype.md` §6.6–6.7 already implements exactly this, in about 40 lines of vectorized NumPy.

Building `ghost_cells`, `neighbor_map`, and MPI-style `exchange_boundary_data` for a field with no neighbor-dependence is solving a problem that doesn't exist here.

## 2. Direct conflicts with ratified decisions

| ADR | Decision | What `pipeline-idea-v1.md` proposes instead |
| --- | --- | --- |
| **ADR-005** | Python (NumPy/SciPy/pandas/astropy) + Plotly for Phase 0; explicitly *"Rules out: Starting in JavaScript/Three.js before the model is validated."* | "Python only for orchestration/analysis, not the hot loop"; core simulation in **C++/CUDA** from day one, i.e. skip straight past Phase 0's entire purpose. |
| **ADR-004** | Dual-regime handling: a smooth statistical field at galactic scale (one 300×300 grid) and discrete point sources only in local-zoom views (one 200×200 grid) — two small, fixed, independently-evaluated grids. | A single generalized chunked/tiled/sparse-adaptive grid with GPU-resident dirty-chunk tracking and refine/coarsen logic — solving a scale problem (huge adaptive domains) this project doesn't have, since it deliberately never puts point hazards on the galactic grid at all. |
| **ADR-006** | Specify the model, entity schema, equation set, and build plan fully *before* implementing; the model's correctness is the risk, not the graphics. | A stack and architecture proposal that never references the model at all — no log-odds, no factor registry, no entity schema, no equation ID. It specifies compute infrastructure for an unspecified computation. |
| **ADR-011** | Every veil value carries a **parallel confidence channel** (`EQ-CORE-4`) propagated to a canonical blue→purple→red hue, independent of height `H`. | No concept of a second, confidence-valued field anywhere in the document. The renderer sections only discuss extracting geometry from a single scalar field — the entire provenance/honesty system, which `DECISIONS.md` calls "the project's defining principle," is absent. |
| **ADR-012** | Layered storage already decided: `staging/{source}` and `entities` as **Parquet**, `field_provenance` as a long-format audit ledger, `veil_field` as **NumPy → Zarr/NetCDF**, `spatial_index` via **SciPy `cKDTree`**. No database server required. | A parallel, uncoordinated storage design: **HDF5**, **Apache Arrow**, **ZeroMQ**, **MPI**-distributed checkpoints — none of which map onto or reference the already-specified ingest/canonical/derived layering. |

## 3. Scale mismatch

The document's justification for GPU/C++/MPI is implicitly "very high-volume data" and "huge" domains. The actual numbers, from `plan-phase0-veil-prototype.md`:

- Galactic-scale grid: **300×300 = 90,000 cells**, evaluated once per requested time step.
- Local-zoom grid: **200×200 = 40,000 cells**.
- Phase 0 star catalog: **~100k–2.5M rows** (AT-HYG).
- Phase 0 hazard sources: **~10–20 hand-picked stars**.
- Even at full Phase 3 scale (Gaia DR3, ~1.8 billion rows), the roadmap's own answer is **out-of-core dataframes (Dask/Vaex) at the ingestion boundary only** — not a rearchitecture of the field computation itself. The field evaluation stays a cheap vectorized map over a modest grid regardless of catalog size, because the grid resolution is fixed by the dual-regime decision (ADR-004), not by row count.

None of these numbers approach the territory where a C++/CUDA/MPI/domain-decomposition stack pays for itself. A 90,000-cell NumPy `expit()` call over a handful of vectorized factor terms runs in milliseconds on a laptop.

## 4. What the proposal never engages with

Beyond the ADR conflicts above, the document is silent on requirements that are load-bearing elsewhere in the project:

- **Entity clickability.** `spec-galactic-habitability-veil.md` and the Phase 0/1 plans require hovering/clicking an entity to show its data (raycasting in Three.js, `hovertext` in Plotly). The proposed renderer only discusses `mesh_generation` from field deltas — there's no entity layer, no metadata channel, nothing to click.
- **Provenance/speculative flagging.** `entity.md` and `schema-field-definition.md` require every field to carry a `(provenance_tier, confidence)` pair through to rendering. The proposal's `FrameDelta`/`FramePacket` structures carry only compressed field values.
- **The two-store equation split (ADR-011).** Certainty is structural in this project — which *file* an equation lives in (`equations-core.md` vs. `equations-provisional.md`) *is* its trust classification. Nothing in a C++ simulation core naturally expresses "this term's certainty is defined by which markdown file its Python counterpart is documented in"; the proposal doesn't attempt to carry that classification through at all.

## 5. Wrong technique even on its own terms

Setting the scale mismatch aside, several specific technique choices don't fit the actual output shape:

- **Marching cubes / dual contouring** extract a surface from a *volumetric* scalar field (isosurfacing). The Drake Display's veil is explicitly a **2.5D height field over the disk plane** (`spec-galactic-habitability-veil.md`, `plan-phase0-veil-prototype.md` §1: *"a galactic-scale 2.5D veil surface over the disk plane"*) — a heightmap, rendered directly as `Surface(x=X, y=Y, z=H)` in Plotly today and as a deformed mesh from the same `(x, y, H)` grid in Three.js/deck.gl at Phase 1. There is no isosurface to extract; the "mesh" is just the grid itself with per-vertex height. Marching cubes is solving a problem (surface extraction from a 3D volume) this project's output shape doesn't have.
- **Signed distance fields (SDF)** are for representing solid geometry implicitly (offsets, boolean unions, ray-marched rendering). Nothing in this project's model — a probability height field — benefits from an SDF representation.
- **Unity/Unreal** would introduce a second full game-engine toolchain and licensing regime on top of the already-decided web stack (Three.js/deck.gl, ADR-005/roadmap Phase 1), for a browser-deliverable, hobbyist-scale visualization tool. The roadmap already has a lighter, decided answer.

## 6. Document-quality issues, separate from the architecture itself

Independent of whether the recommendations are right, the document itself has a structural problem: it restates essentially the same C++/CUDA/MPI/Zarr/marching-cubes recommendation **at least five times** under different headings ("Best architecture," "Implementation Suggestions," "Recommended architecture," "Recommended stacks," "My recommendation," "High-level layout"), followed by ~35 near-duplicate pseudocode blocks that re-describe the same chunk/update/stream/checkpoint loop at increasing levels of (still generic) detail. It never cites a single file, equation ID, factor name, or ADR from this repository — it would be equally applicable, unchanged, to any large-scale grid-based physics simulation project. That's a strong signal it was pasted in from a general-purpose "how to build a fast field simulation" answer rather than written against this project's actual specification, which directly conflicts with ADR-006's requirement to specify against the model, not against a generic template.

## 7. What's actually salvageable

A few individual technologies mentioned do overlap with the project's real future direction — but all of them are already specified, better, elsewhere:

- **Zarr for large chunked field snapshots** — already the designated Phase-3+ successor to in-memory NumPy for `veil_field`, per `data-store-schema.md`/ADR-012.
- **Out-of-core dataframes (Dask/Vaex)** — already the designated Phase 3 answer for Gaia-scale ingestion, per `roadmap-veil-project.md` and `plan-phase0-veil-prototype.md` §3.4.
- **A WebGL-family renderer** — already the designated Phase 1 target (Three.js/WebGL or deck.gl), per ADR-005 and the roadmap.

Nothing else in the document is additive; picking these three ideas out doesn't require adopting any of the C++/CUDA/MPI/HDF5/Arrow/Unity apparatus around them.

## 8. Recommendation

Do not adopt this as the pipeline architecture. Follow the existing, already-specified path instead: finish Phase 0 in Python/NumPy/SciPy/pandas/astropy/Plotly per `plan-phase0-veil-prototype.md`, move rendering only (not the model) to Three.js/deck.gl in Phase 1, add population synthesis in Phase 2, and add out-of-core ingestion (Dask/Vaex) plus the Zarr-backed derived store in Phase 3 — all per the roadmap already in the repository.

If a genuine real-time performance wall is hit at Phase 4+ scale (which is plausible only once the field is being recomputed at interactive frame rates for a fully populated, real-data-scale galaxy), the narrow fix is GPU compute *inside the existing WebGL renderer* (e.g. evaluating the factor sum in a fragment/compute shader against data already resident on the GPU) — not a ground-up rewrite of the simulation core in C++/CUDA with an MPI cluster and a second rendering engine. That bridge is a long way off and shouldn't be built before the model itself — the project's actual identified risk, per ADR-006 — is even validated.
