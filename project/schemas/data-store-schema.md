# Schema: Data Store — The Drake Display

> **The canonical description of the project's data stores and how ingested/processed data is laid out in them.** It standardizes how any store is described *and* specifies the concrete stores the project uses. Built on the layered storage architecture decided in **ADR-012**, and on `schema-field-definition.md` (per-field confidence), `data-source-info-schema.md` (source field maps), and `entity.md` (entity content). Governed by `SCHEMAS.md`.

---

## 1. The storage architecture (ADR-012)

Data **arrives by source** but is **consumed by entity**, and confidence is **per-field, per-source**. This forces a layered design — three stores, three organizing principles:

```
[ sources ] → INGEST (by source) → CANONICAL (by entity, per-field provenance) → DERIVED (by space-time)
                staging/{source}        entities  (+ field_provenance ledger)      veil_field + spatial_index
```

- **Ingest** preserves provenance and is what you re-process from.
- **Canonical** is the model's single source of truth for entities; entity-oriented so consumers never change.
- **Derived** holds the computed veil field and fast-lookup indices; the field is arrays, not rows.

## 2. Store descriptor (how to describe any store)

Every store is described by:

| Attribute | Meaning |
|---|---|
| `store_id` | Stable identifier |
| `layer` | `ingest` / `canonical` / `derived` |
| `organized_by` | `source` / `entity` / `space-time grid` / `spatial index` |
| `grain` | What one record represents |
| `format` | Physical format (Parquet, Zarr/NumPy, in-memory, DB) |
| `key` | Primary key |
| `contents` | What it holds |
| `provenance_handling` | How per-field source + tier + confidence is stored |
| `indexing` | Spatial / temporal / none |
| `consumers` | What reads it |
| `refresh` | How/when it is (re)built |

## 3. The concrete stores

### `staging/{source}` — ingest layer
- **layer:** ingest · **organized_by:** source · **grain:** one row per source record
- **format:** Parquet (one dataset per source) · **key:** source-native ID
- **contents:** original columns, verbatim, plus the source's per-field confidences from its `data-source-info-schema.md` field map.
- **provenance_handling:** intrinsic — the store *is* the source of record.
- **consumers:** the entity-resolution step. · **refresh:** on new source release; immutable snapshots per version.

### `entities` — canonical layer (the model's source of truth)
- **layer:** canonical · **organized_by:** entity · **grain:** one row per resolved entity
- **format:** Parquet (wide) · **key:** `entity.id`
- **contents:** all fields from `entity.md`, entity-resolved across sources.
- **provenance_handling (the crux):** each physical field `X` is stored not as a bare value but as a **cell** — value plus companion attributes `X__source`, `X__tier`, `X__confidence` (companion columns in Phase 0; a nested struct later). The *surfaced* value is the highest-confidence one; conflict rule in §4.
- **indexing:** by `id`; galactocentric coordinates present for spatial build.
- **consumers:** field computation (`factors.py`), the renderer's entity layer, click-to-info. · **refresh:** rebuilt when staging changes.

### `field_provenance` — canonical layer (audit ledger, long format)
- **layer:** canonical · **organized_by:** entity×field×source · **grain:** one row per `(entity_id, field, source)`
- **format:** Parquet (long) · **key:** composite
- **contents:** `entity_id, field, value, source, provenance_tier, confidence`. Retains *every* source's value for a field, including the non-surfaced ones.
- **purpose:** full auditability and the detail behind the blue/purple/red shading; makes conflict resolution transparent and reversible. · **consumers:** audit tooling, provenance drill-down.

### `veil_field` — derived layer (NOT entity data)
- **layer:** derived · **organized_by:** space-time grid · **grain:** one grid cell per timestep
- **format:** chunked arrays — NumPy in Phase 0, **Zarr/NetCDF** later (built for chunked, time-sliceable N-d arrays; ideal for scrubbing the fourth dimension)
- **contents:** `H(x,y,z,t)` (veil height) and `confidence_here(x,y,z,t)` (from `EQ-CORE-4`), per cell per timestep, at both galactic-scale and local-zoom resolutions (dual-regime, ADR-004).
- **consumers:** the renderer's surface layer. · **refresh:** recomputed from `entities` + `factors.md` when factors/time change.

### `spatial_index` — derived/serving layer
- **layer:** derived · **organized_by:** spatial index · **grain:** entity position
- **format:** in-memory k-d tree / octree (SciPy `cKDTree` in Phase 0)
- **contents:** entity positions keyed to `entity.id`, for fast click/hover pick and radius queries (also used by point-hazard factors).
- **consumers:** interaction layer, `factors.py` point-hazard falloff. · **refresh:** rebuilt with `entities`.

## 4. Conflict resolution (multi-source fields)

When several sources supply the same field for the same entity:
1. **Surface** the value with the highest `confidence` in the `entities` store.
2. Break ties by `provenance_tier` (Measured > Inferred > Statistical > Modeled > Speculative), then by source recency.
3. **Retain all** candidate values in `field_provenance`.
4. If no source supplies a field, it is **absent → default confidence 0.10 (Speculative)** per `schema-field-definition.md`; never fabricated.

## 5. Phase 0 realization (keep it minimal)
- `staging/{source}`, `entities`, `field_provenance` → **Parquet files** (readable by pandas; DuckDB is the natural next step for querying at scale — embedded, columnar, reads Parquet directly).
- `veil_field` → **NumPy arrays** in memory/`.npz`; adopt Zarr when the 4D grid outgrows RAM.
- `spatial_index` → **SciPy `cKDTree`**, rebuilt at load.
- No database server is required for Phase 0; every store is a file or an in-memory structure.

## 6. Why this shape (the guarantees it preserves)
- **Consumers don't change:** the model reads one entity-oriented canonical store, exactly as ADR-011 required.
- **Provenance is never lost:** ingest snapshots + the field-provenance ledger make every surfaced value traceable and every conflict reversible.
- **Confidence flows end-to-end:** per-field confidences (from source field maps) → cells in `entities` → `EQ-CORE-4` → `confidence_here` in `veil_field` → blue/purple/red on screen.
- **Entities and fields are stored in their natural shapes:** point data in a spatial index, the scalar field in grids — the dual-regime honored at the storage layer.
