# Pipeline v2 — An End-to-End Architecture for the Veil, Grounded in the Actual Model

> This is a full ingestion-to-render pipeline proposal, written directly against the project's own specification: `DECISIONS.md`, `equations-core.md`, `equations-provisional.md`, `factors.md`, `entity.md`, `data-store-schema.md`, `plan-phase0-veil-prototype.md`, and `roadmap-veil-project.md`. Where those documents already answer a question, this document points to them rather than re-deciding it — the goal here is to give the *whole pipeline*, across all five phases, one coherent narrative, since today that story is split across several phase- and component-specific documents. See `pipeline-v1-assessment.md` for why the earlier draft (`pipeline-idea-v1.md`) is not that narrative.

---

## 1. What kind of computation this actually is

Before any stack choice: the veil field `H(x, y, z, t)` is **not** a simulation with time-evolving neighbor-coupled state. Per `EQ-CORE-1`–`EQ-CORE-3`, every point's value is a closed-form function of its own position, the time `t`, and the properties of nearby/relevant entities:

```text
ℓᵢ(point, t) = signᵢ · wᵢ · Mᵢ · fᵢ(space) · gᵢ(t)
logit(H) = B₀ + Σᵢ ℓᵢ
H = expit(logit(H))
```

No point's value depends on another point's *previous* value. This makes the whole field a **map**: evaluate 17 independent, closed-form factor functions (`factors.md` §2) over a grid, sum in log-odds space, and pass through a logistic. That's it. The entire pipeline exists to (a) get clean, correctly-transformed entity data into the factor functions' inputs, (b) evaluate that map efficiently at two grid resolutions (ADR-004), (c) carry a parallel confidence value through the same map (ADR-011), and (d) render both. Nothing here calls for time-integration, stencils, ghost cells, or inter-chunk communication — vectorized array math is sufficient at every phase, including at Gaia scale.

## 2. End-to-end pipeline overview

```text
┌─────────────┐   ┌──────────────┐   ┌───────────────┐   ┌────────────────┐
│  RAW SOURCES │──▶│   INGEST     │──▶│  TRANSFORM &   │──▶│    ENTITIES     │
│ (AT-HYG,     │   │ (per-source, │   │  RESOLVE       │   │  (canonical,     │
│  Exoplanet   │   │  Parquet     │   │ (galactocentric│   │  one row/entity, │
│  Archive,    │   │  staging,    │   │  coords, cross-│   │  provenance +    │
│  hazard      │   │  field-map   │   │  match, dedupe)│   │  confidence per  │
│  catalogs)   │   │  confidences)│   │                │   │  field)          │
└─────────────┘   └──────────────┘   └───────────────┘   └────────┬────────┘
                                                                    │
                                                                    ▼
┌────────────────┐   ┌──────────────────┐   ┌───────────────────────────────┐
│  RENDER LAYER   │◀──│  DERIVED STORE   │◀──│      FIELD EVALUATION          │
│ (Plotly Phase 0;│   │ (veil_field:     │   │  factor_registry (factors.md)  │
│  Three.js/deck. │   │  NumPy→Zarr;     │   │  × dual-regime grids (ADR-004) │
│  gl Phase 1+;   │   │  spatial_index:  │   │  → H(x,y,z,t)  [height]        │
│  entity click/  │   │  cKDTree)        │   │  → confidence_here(x,y,z,t)    │
│  hover from      │   │                  │   │     [EQ-CORE-4, hue]          │
│  ENTITIES)       │   └──────────────────┘   └───────────────────────────────┘
└─────────────────┘
```

Two things run in parallel through the whole right-hand side of this diagram, per ADR-011: the **height** field (`H`, what the surface looks like) and the **confidence** field (`confidence_here`, what color it's rendered — blue→purple→red). They share the same factor contributions `ℓᵢ` but are two separate reductions over them (§3.4).

## 3. Stage-by-stage architecture

### 3.1 Ingestion — organized by source

Matches ADR-012 exactly; nothing new proposed here. Each source (`AT-HYG`, `NASA Exoplanet Archive`, a hand-built hazard list in Phase 0; Gaia/APOGEE/GALAH from Phase 3) lands in `staging/{source}` as **Parquet**, columns untouched, plus the per-field `(provenance_tier, confidence)` pairs from that source's `data-source-info-schema.md` field map. Phase 0 reads static CSV downloads (`plan-phase0-veil-prototype.md` §6.2); Phase 3 adds `astroquery` and out-of-core ingestion via **Dask** or **Vaex** for Gaia-scale pulls — the ingestion *mechanism* changes with scale, the staging *shape* does not.

### 3.2 Transform & resolve — coordinates, cross-matching, one row per entity

1. **Coordinate transform** (`EQ-GEO-1`/`EQ-GEO-2`/`EQ-GEO-3`): every entity's native RA/Dec/distance goes through `astropy`'s `SkyCoord` → `Galactocentric` to produce `(x, y, z)` in kpc, exactly as specified in `plan-phase0-veil-prototype.md` §6.4. Never reuse a catalog's native Cartesian columns (ADR-003).
2. **Entity resolution**: where the same physical object appears in multiple sources (a star in both AT-HYG and, later, Gaia), merge to one canonical row, surfacing the highest-confidence value per field and retaining every source's value in `field_provenance` (ADR-012). Phase 0 has no cross-source overlap to resolve yet (single star source); the resolution step is a no-op until Phase 3, but the schema is shaped for it from day one so nothing downstream has to change later.
3. Output: the **`entities`** canonical Parquet store, one row per entity, each field a *cell* — `value`, `source`, `provenance_tier`, `confidence` — per `schema-field-definition.md`.

### 3.3 Factor registry & field evaluation — the actual math

This is `factors.py` + `field.py` from `plan-phase0-veil-prototype.md` §6.6–6.7, unchanged in kind at every phase — only the entity table feeding it grows:

1. Build the **factor registry**: 17 `Factor` objects per `factors.md` §2, each carrying `sign`, `backing (w)`, `magnitude (M)`, a spatial profile `f` from the shared library (`P-RADIAL`, `P-DISKDENS`, `P-POINT`, …), and a temporal profile `g` (`G-STATIC`, `G-RAMP-SPIKE-DECAY`, …).
2. Evaluate on **two grids**, per ADR-004 — never one generalized adaptive grid:
   - **Galactic-scale** — coarse (300×300 in Phase 0), covers the whole disk, only `Galactic-smooth` and `Global-temporal` regime factors active.
   - **Local-zoom** — fine (200×200 in Phase 0), covers a small patch, adds `Local-point` and `Stellar-property` regime factors for the entities in view.
3. Sum contributions in log-odds space and apply `expit` (`EQ-CORE-1`/`EQ-CORE-2`) → `H` in `(0, 1)`.

All of this is vectorized NumPy array math today; nothing about moving to Gaia-scale *data* changes this step's cost, because grid resolution — not catalog size — sets the compute cost of field evaluation. A bigger entity table means more rows feeding `Local-point`/`Stellar-property` factors near the camera, not a bigger grid.

### 3.4 Confidence propagation — the parallel channel v1 never had

Per `EQ-CORE-4` (`equations-provisional.md`), evaluated alongside §3.3, not after it:

1. **Per-factor input confidence** — for each factor, the minimum `confidence` across the entity fields it reads (weakest link).
2. **Per-factor confidence** — that minimum, scaled by the factor's own `backing (w)`.
3. **Location confidence** — the magnitude-weighted mean of per-factor confidence, weighted by each factor's `|ℓᵢ|` contribution to the log-odds sum at that point.
4. **Render** — map `confidence_here` onto the canonical blue(1.0)→purple(0.5)→red(0.0) hue scale, independent of `H`. A point can be a high, uncertain hill (bright, red) or a low, well-established dip (dark, blue) — the two channels are orthogonal.

This must be implemented as a second array output from the same factor-evaluation pass (`H_grid`, `confidence_grid = habitability_field_with_confidence(...)`), not bolted on afterward — every render surface downstream needs both.

### 3.5 Storage — the derived layer

Unchanged from ADR-012 / `data-store-schema.md`: `veil_field` (the `H` and `confidence_here` arrays together, keyed by grid + timestep) as **NumPy in Phase 0**, migrating to **Zarr** once the time axis and full-galaxy population make in-memory storage impractical (Phase 2+). `spatial_index` (for entity picking/hover) as **SciPy `cKDTree`**, rebuilt at load. No database server at any phase — Parquet + DuckDB (for ad hoc querying once `entities`/`field_provenance` grow past comfortable pandas size) covers everything.

### 3.6 Rendering & interaction — phase-appropriate, one source of truth

The field model (§3.3–3.4) is the single source of truth at every phase; only the renderer changes:

- **Phase 0** — `matplotlib` for fast static validation, **Plotly** `Surface` for the interactive veil (height from `H`, colorscale from `confidence_here`), `Scatter3d` + `hovertext` for entity info, a `sliders` control for time. Output: one self-contained HTML file. (`plan-phase0-veil-prototype.md` §6.9–6.10.)
- **Phase 1** — swap the renderer only, to **Three.js/WebGL** or **deck.gl**, consuming the same `(X, Y, H, confidence)` grids (precomputed to JSON, or served over a small local API). Add raycasting for click-to-info on entities, full orbit/free-flight camera. The factor registry and field math do not move to JavaScript — they stay Python, server-side or precomputed, exactly as `plan-phase0-veil-prototype.md` §10 already specifies.
- **Phase 2** — the renderer now scrubs a precomputed *sequence* of `(H, confidence)` frames across cosmic time, driven by per-entity temporal state functions; population synthesis (TRILEGAL-style) fills the entity table for unobserved regions before this step, not inside the renderer.
- **Phase 3** — no renderer change; the entity table underneath gets bigger and more measured (Gaia/APOGEE/GALAH), and a provenance/confidence overlay becomes visually meaningful at scale for the first time.
- **Phase 4** — polish only: live factor-weight tuning UI, scenario save/load, performance passes on the existing stack.

## 4. Phase-by-phase stack (one narrative, not five separate decisions)

- **Phase 0:** Python 3.11+, NumPy, SciPy, pandas, astropy, matplotlib, Plotly. (ADR-005.)
- **Phase 1:** + Three.js/WebGL or deck.gl for rendering only. Field model stays Python/portable (precomputed JSON or a thin local API).
- **Phase 2:** + population-synthesis tooling (TRILEGAL-style) at the ingestion boundary; per-entity temporal state functions in the existing factor/field layer.
- **Phase 3:** + astroquery, Dask/Vaex for out-of-core ingestion at Gaia scale; Zarr/NetCDF for the derived `veil_field` store once it outgrows RAM; DuckDB for ad hoc querying of `entities`/`field_provenance` at scale.
- **Phase 4:** no new core dependencies; UI and packaging work on top of the above.

Nothing here is new relative to `DECISIONS.md`/`roadmap-veil-project.md` — this table exists so the *whole* pipeline's dependency story is readable in one place instead of reconstructed by reading five documents.

## 5. Concrete data-flow pseudocode

Kept short and specific to this project's real functions — not a generic simulation-loop template.

```python
# main.py — Phase 0 entry point, extends cleanly at later phases

entities = ingest.load_entities(source_paths)              # pandas, per-source Parquet staging
entities = coords.attach_galactocentric(entities)           # astropy: RA/Dec/dist -> x,y,z (kpc)
entities = resolve.merge_by_entity(entities)                 # no-op until Phase 3 multi-source overlap

registry = factors.build_registry(config)                    # factors.md's 17 Factor objects

for t in time_steps:
    grids = field.make_grids(entities, config)                # galactic-scale + local-zoom (ADR-004)
    H, confidence = field.evaluate(registry, grids, entities, t)
    store.write_veil_frame(t, H, confidence)                  # NumPy now, Zarr later

render.emit(store, entities, spatial_index.build(entities))   # Plotly now, WebGL renderer later
```

```python
# field.py — the actual "hot loop," and it's just array math

def evaluate(registry, grids, entities, t):
    logit = np.full(grids.shape, B0)
    weighted_confidence_sum = np.zeros(grids.shape)
    weight_sum = np.zeros(grids.shape)

    for factor in registry:
        l_i = factor.logit_contribution(grids, entities, t)      # EQ-CORE-3, vectorized
        c_i = factor.confidence(entities)                        # EQ-CORE-4 step 1-2, weakest link x w
        logit += l_i
        weighted_confidence_sum += c_i * np.abs(l_i)
        weight_sum += np.abs(l_i)

    H = expit(logit)                                             # EQ-CORE-2
    confidence_here = np.where(weight_sum > 0,
                                weighted_confidence_sum / weight_sum,
                                BASELINE_CONFIDENCE)               # EQ-CORE-4 step 3
    return H, confidence_here
```

No loop over grid cells, no neighbor reads, no boundary exchange — every line is an array-wide operation. This is the whole "hot loop," at every project phase.

## 6. Module / file layout

Extends the structure already defined in `plan-phase0-veil-prototype.md` §7, generalized past Phase 0 rather than replaced:

```text
veil/
├── data/
│   ├── raw/                  # static downloads (Phase 0) or cache of API pulls (Phase 3+)
│   ├── staging/{source}/     # per-source Parquet, ADR-012
│   └── entities/             # canonical Parquet + field_provenance ledger
├── src/
│   ├── config.py             # constants: R_sun, gradients, grid extents, factor weights
│   ├── ingest.py             # per-source load + clean -> staging
│   ├── coords.py             # astropy RA/Dec/dist -> galactocentric xyz
│   ├── resolve.py            # cross-source entity resolution (no-op pre-Phase-3)
│   ├── factors.py            # Factor dataclass + factors.md's registry + shared profile library
│   ├── field.py              # dual-regime grids, evaluate() -> (H, confidence_here)
│   ├── store.py               # veil_field read/write: NumPy (P0) -> Zarr/NetCDF (P3+)
│   ├── spatial_index.py       # cKDTree build/query for entity picking
│   └── render/
│       ├── plotly_render.py   # Phase 0 renderer
│       └── web_bridge.py      # Phase 1+: serializes (X, Y, H, confidence, entities) for the JS renderer
├── web/                        # Phase 1+ only: Three.js/deck.gl app, consumes web_bridge output
├── requirements.txt
└── README.md
```

Same module boundaries `plan-phase0-veil-prototype.md` already established (ingest / coords / factors / field / render each independently swappable); this just names where cross-source resolution, the confidence-aware store, and the eventual web bridge slot in, so Phase 1–3 additions don't require restructuring Phase 0's code.

## 7. Where real scaling concerns might eventually bite

Named narrowly, and deliberately not designed for yet:

- **If** Phase 4+ needs the field recomputed at true interactive frame rates against a fully populated, Gaia-scale entity table (many more `Local-point`/`Stellar-property` factor evaluations per frame near the camera), the first lever is pushing the §3.3 evaluation into a **WebGL compute/fragment shader** inside the already-chosen Phase 1 renderer — data already resident on the GPU for rendering gets evaluated there too. That is a shader added to the existing Three.js/deck.gl app, not a new language, build system, or process architecture.
- **If** the derived `veil_field` store genuinely outgrows what Zarr-on-disk can serve interactively, that's a caching/tiling problem at the storage layer (§3.5), solvable within the existing Parquet/Zarr/DuckDB stack — not a reason to introduce a distributed simulation core.

Neither is close to being the current bottleneck (§1); both are called out here only so a future phase doesn't have to rediscover that the fix is narrow, not architectural.

## 8. Explicit non-goals

Stated plainly so a future proposal doesn't reintroduce them without a concrete, measured reason:

- No PDE solver, finite-difference/finite-volume scheme, or neighbor-stencil update — the field has no neighbor-dependent state (§1).
- No C++/CUDA/MPI simulation core, no domain decomposition, no ghost-cell boundary exchange.
- No marching cubes / dual contouring / signed distance fields — the veil is a 2.5D height field rendered directly as a heightmap, not a volumetric isosurface.
- No HDF5, Apache Arrow, or ZeroMQ — the storage and IPC story is already closed by ADR-012 (Parquet/DuckDB/Zarr) and, within a single process or a JS↔Python bridge, doesn't need a message-queue layer.
- No Unity/Unreal — the rendering target is a browser app (Three.js/deck.gl), per ADR-005 and the roadmap.
