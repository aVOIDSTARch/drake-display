# Plan: Phase 0 — Galactic Habitability Veil Prototype (Self-Contained Build Spec)

> This document is written to be implementable **without further consultation** by a competent developer or coding agent. It specifies scope, stack, architecture, every build step, the mathematics, reference code for the non-obvious parts, and objective acceptance criteria. It assumes the conceptual model from `spec-galactic-habitability-veil.md` and the data sources from `data-sources-catalog.md`, but restates everything needed so it can stand alone. Rationale is given for each choice; where a reasonable alternative exists, it is named and the reason for rejection stated.

---

## 1. Purpose and scope

**Phase 0 exists to prove three things and nothing more:**

1. That the **log-odds factor model** correctly combines multiple positive/negative habitability factors into a valid probability field (compounding at overlaps without breaking bounds).
2. That real catalog data can be **ingested, coordinate-transformed, and joined** into a unified entity table that drives the field.
3. That a **time parameter** can evolve at least one hazard factor so its "dip" deepens toward a discrete catastrophic moment — demonstrating the 4D concept at a small scale.

**Explicitly OUT of scope for Phase 0** (deferred to later phases, to prevent scope creep):

- Full WebGL/browser 3D with free-flight camera (Phase 1).
- Procedural whole-galaxy population synthesis (Phase 2).
- Real per-star spectroscopic metallicity ingestion at scale (Phase 3).
- Persistence, user accounts, scenario saving, polished UI.

**Deliverable:** a Python program (runnable from a single entry point) that produces (a) a galactic-scale 2.5D veil surface over the disk plane, and (b) a local zoomed demonstration in which an individual massive star's habitability dip deepens as a time slider advances toward its core collapse. Both rendered interactively (rotate/zoom/hover/slide) in a browser via Plotly, with matplotlib used for fast static validation.

---

## 2. Guiding design principles

- **Prove the model before polishing the render.** The intellectual risk is in the math and data plumbing, not the graphics. This is why Phase 0 is Python, not JavaScript.
- **Vectorize everything over the grid.** The field is evaluated on a grid of thousands to millions of cells; Python-level loops over cells are unacceptably slow. All field math must be NumPy array operations.
- **Separate the four concerns cleanly:** data ingestion, coordinate handling, the factor/field model, and rendering. Each is a module with a defined interface so any one can be swapped (e.g., renderer replaced in Phase 1) without touching the others.
- **Encode confidence, not just value.** Every factor carries a science-backing weight; the model must keep that weight as a first-class multiplier so the output can later be shown as "how much do we trust this height."
- **Honesty of provenance.** Even in Phase 0, keep a flag distinguishing real-data-driven contributions from hard-coded/speculative ones, so the render can later be made to show it.

---

## 3. Technology stack and rationale

### 3.1 Language: Python 3.11+

**Why:** Astronomy's data ecosystem is Python-native (astropy, astroquery, and every survey's client tooling). For a prototype whose risk is data-wrangling and numerical modeling, Python offers the shortest path from raw CSV to validated field. Its scientific stack (NumPy/SciPy/pandas) is mature and vectorized.
**Why not JavaScript/TypeScript now:** JS is the right choice for the *interactive 3D* target (Phase 1, via Three.js/WebGL), but starting there forces you to solve rendering before the model is proven, and the data-science ergonomics are far worse. Defer JS to Phase 1.
**Why not Julia/R:** Julia is fast but has a thinner astronomy-tooling ecosystem and steeper onboarding for a handoff; R is statistics-first and weak for 3D geometry and coordinate transforms. Python is the pragmatic center of mass.
**Version:** 3.11+ for performance and modern typing; pin it in the environment for reproducibility.

### 3.2 Core libraries (required)

- **NumPy** — the numerical substrate. The veil field is a NumPy array; all factor contributions are computed as vectorized array math. *Required because* per-cell Python loops would make even a modest grid take minutes per time step.
- **pandas** — catalog ingestion, cleaning, joining, schema normalization. *Required because* the input data arrives as heterogeneous CSV/VOTable tables that must be filtered, NaN-handled, and merged into one entity table; pandas is the standard tool for exactly this.
- **SciPy** — two specific needs: `scipy.spatial.cKDTree` for efficient radius/nearest-neighbor queries when a point hazard must contribute only to nearby grid cells (avoids an O(N_grid × N_hazards) blowup), and `scipy.special.expit` for the numerically-stable logistic transform. *Required for* performance and numerical safety.
- **astropy** — rigorous coordinate transformation (equatorial ICRS → Galactic → Galactocentric Cartesian) and unit handling. *Required because* the metallicity gradient and all galactocentric-radius-dependent factors are defined in a galaxy-centered frame, while catalogs supply RA/Dec/distance; doing this transform by hand is error-prone and astropy's `SkyCoord`/`Galactocentric` is the validated standard.

### 3.3 Rendering libraries

- **matplotlib** (+ `mpl_toolkits.mplot3d`) — fast, dependency-light static rendering for **validation**: heatmaps, contour plots, and quick 3D surfaces to confirm the field looks right before investing in interactivity. *Required as* the developer's inner-loop sanity check.
- **Plotly** — the **primary interactive renderer** for Phase 0. It provides, from pure Python with no JavaScript: a rotatable/zoomable 3D `Surface` (the veil), hover tooltips on `Scatter3d` entities (the "click an entity → info" seed), and a built-in **slider** for the time axis. *Chosen because* it delivers ~80% of the Phase 1 interactive dream at ~10% of the effort, and keeps the whole prototype in one language. *Why not go straight to Three.js:* unnecessary rendering-engineering overhead before the model is validated. *Why not Bokeh/Vispy:* Plotly's built-in slider + 3D surface + hover combination is the best fit for this specific need with least code.

### 3.4 Optional / deferred libraries

- **astroquery** — programmatic fetch from Gaia/SIMBAD/NASA Exoplanet Archive. *Deferred for Phase 0* in favor of static CSV downloads (reproducibility, no network dependency during development); adopt in Phase 3 when live/large-scale ingestion matters.
- **Dask/Vaex** — out-of-core dataframes for billion-row Gaia data. *Not needed in Phase 0* (we use the ~100k–2.5M-row AT-HYG subset); introduce when scaling past RAM.

---

## 4. Conceptual architecture (data flow)

```text
[ raw catalogs: AT-HYG CSV, Exoplanet Archive CSV, hazard-source list ]
                              │  ingest.py  (pandas: load, clean, filter)
                              ▼
[ per-catalog DataFrames with RA/Dec/distance + properties ]
                              │  coords.py  (astropy: → galactocentric x,y,z in kpc)
                              ▼
[ unified ENTITIES table: id, x, y, z, kind, mass, [Fe/H], t_birth, ... ]
                              │  factors.py  (define Factor objects: M, w, f(d), g(t), sign)
                              ▼
[ FACTOR REGISTRY (list of Factor objects, positive and negative) ]
                              │  field.py  (numpy: evaluate logit over grid at time t; expit → H)
                              ▼
[ H(grid, t): 2D/2.5D scalar probability field ]
                              │  render.py  (matplotlib validate → plotly interactive + slider + hover)
                              ▼
[ interactive veil surface + entity markers + time slider ]
```

Each arrow is a module boundary with a documented function signature (Section 8). The `main.py` entry point wires them together and exposes a couple of config switches (galactic-scale view vs local-zoom demo; time range).

---

## 5. The scale problem — the design decision that shapes everything

This is the single most important thing to understand before writing code, and the reason naive attempts fail.

**Point hazards are tiny relative to the galaxy.** A supernova's lethal radius is ~10 pc = 0.01 kpc. The galactic disk is ~30 kpc across. On a whole-disk grid, an individual supernova's dip is far smaller than one pixel — it would be invisible, and worse, trying to resolve it would demand an absurdly fine grid.

**Therefore Phase 0 operates in two regimes, and you build both:**

1. **Galactic-scale regime (smooth fields).** At whole-disk scale, hazards are represented as **statistical density fields**, not individual objects: e.g., a supernova-hazard field proportional to local stellar density (which rises toward the center), and a metallicity ridge that varies smoothly with galactocentric radius. These smooth fields are what render as the big veil surface. Grid: coarse, e.g., 300×300 cells over a ±20 kpc plane.

2. **Local-zoom regime (individual entities).** To demonstrate the time-slider drama (a massive star's deepening dip), you render a **small patch** — e.g., a 400×400 pc region around a chosen massive star — on a fine grid (say 200×200 cells at ~2 pc resolution) where the individual point hazard's falloff and its `g(t)` evolution are actually visible.

This dual-regime approach is not a compromise; it reflects the real physics (hazards are statistical at galaxy scale, discrete at local scale) and it is the honest way to make both the map and the time animation meaningful. **Do not attempt to show individual supernovae on the full-galaxy grid.**

---

## 6. Detailed build steps

### 6.1 Environment setup

1. Install Python 3.11+.
2. Create an isolated virtual environment (`python -m venv venv`; activate). *Rationale: reproducibility and dependency isolation for handoff.*
3. Install pinned dependencies:

   ```bash
   pip install numpy scipy pandas astropy matplotlib plotly
   ```

4. Record exact versions in `requirements.txt` (`pip freeze > requirements.txt`). *Rationale: another agent must be able to recreate the environment exactly.*

### 6.2 Data acquisition (static downloads for Phase 0)

1. **Stars — AT-HYG database:** download the CSV from the Astronexus HYG GitHub repository (<https://github.com/astronexus/HYG-Database>). Use the augmented (AT-HYG) table for Gaia-enriched coverage, or the classic ~120k HYG table for the smallest, fastest start. Needed columns: an identifier, RA, Dec, distance (or parallax), apparent/absolute magnitude, color index or spectral type.
2. **Planets — NASA Exoplanet Archive:** download the "Planetary Systems" table as CSV (<https://exoplanetarchive.ipac.caltech.edu>). Needed columns: host name, RA, Dec, distance, and (optionally) insolation/equilibrium temperature for habitable-zone flagging.
3. **Hazard sources — a small hand-built list for Phase 0:** create a CSV of ~10–20 massive stars (O/B/Wolf-Rayet) with RA, Dec, distance, and estimated mass, drawn from any Wolf-Rayet/massive-star catalog via VizieR. For a first run, even hard-coded plausible values are acceptable (flag them as speculative). *Rationale: the hazard time-evolution demo needs only a few objects; a full catalog is Phase 2.*
4. Place all files under `data/raw/`.

### 6.3 Ingestion and cleaning (`ingest.py`)

1. Load each CSV with pandas.
2. Filter out rows lacking the required astrometry (no distance/parallax → cannot place in 3D). Drop or flag NaNs explicitly; never silently propagate them into the field math.
3. Derive distance from parallax where needed: `distance_pc = 1000 / parallax_mas` (guard against non-positive parallax).
4. Estimate stellar mass where absent: for main-sequence stars, a crude mass–luminosity or spectral-type→mass mapping is adequate for Phase 0 (flag as approximate). Mass is needed for the main-sequence-lifetime clock (6.8).
5. Return clean, typed DataFrames.
*Rationale: the quality of every downstream result is capped by ingestion hygiene; explicit NaN handling prevents silent corruption of the field.*

### 6.4 Coordinate transformation (`coords.py`)

Convert every entity's (RA, Dec, distance) into **galactocentric Cartesian (x, y, z) in kiloparsecs**, using astropy:

```python
from astropy.coordinates import SkyCoord, Galactocentric
import astropy.units as u

def to_galactocentric(ra_deg, dec_deg, dist_pc):
    c = SkyCoord(ra=ra_deg*u.deg, dec=dec_deg*u.deg,
                 distance=dist_pc*u.pc, frame='icrs')
    g = c.transform_to(Galactocentric())   # Sun placed per astropy defaults
    return (g.x.to(u.kpc).value, g.y.to(u.kpc).value, g.z.to(u.kpc).value)
```

*Rationale: the metallicity gradient and density-based hazard fields are functions of galactocentric radius R = sqrt(x²+y²); they are meaningless in the heliocentric equatorial frame the catalogs supply. astropy's `Galactocentric` frame applies the accepted solar position and orientation so results are physically correct rather than ad hoc. Do NOT reuse HYG's raw x/y/z columns, which are in a heliocentric equatorial frame with a different orientation.*

### 6.5 Unified entity table (`ingest.py` output)

Produce one pandas DataFrame with a common schema, one row per entity:
`id | kind | x_kpc | y_kpc | z_kpc | mass_msun | feh | t_birth_myr | is_speculative`

- `kind` ∈ {star, planet_host, hazard_massive_star, ...}.
- `feh` (metallicity) may be filled from a modeled gradient in Phase 0 (6.6) rather than measured.
- `t_birth_myr` assigned to hazard stars to drive the clock (6.8).
*Rationale: a single normalized table lets the factor model iterate over entities uniformly and lets the renderer attach hover metadata by row.*

### 6.6 The factor model (`factors.py`) — the mathematical core

Implement the **log-odds** combination so factors compound multiplicatively in odds space and the result is always a valid probability. Represent each factor as an object carrying its magnitude, backing weight, spatial profile, temporal profile, and sign.

```python
from dataclasses import dataclass
from typing import Callable
import numpy as np

@dataclass
class Factor:
    name: str
    sign: float          # +1 raises habitability, -1 lowers
    magnitude: float     # M: base strength (tune)
    backing: float       # w in [0,1]: science-confidence weight
    spatial: Callable    # f(dist_or_position_grids) -> array of [0,1] influence
    temporal: Callable   # g(t) -> scalar in [0,1] (or [0,∞) for spikes)

    def logit_contribution(self, grids, t):
        # grids: whatever the spatial fn needs (e.g., R grid, or dx,dy to a source)
        return self.sign * self.backing * self.magnitude * self.spatial(grids) * self.temporal(t)
```

Combine and transform:

```python
from scipy.special import expit  # numerically stable logistic

def habitability_field(factor_list, grids_per_factor, t, baseline_logit=0.0):
    logit = np.full_like(next(iter(grids_per_factor.values())), baseline_logit, dtype=float)
    for f in factor_list:
        logit = logit + f.logit_contribution(grids_per_factor[f.name], t)
    return expit(logit)   # H in (0,1)
```

*Rationale for log-odds: linear addition/subtraction of "heights" overflows the [0,1] range at overlaps and makes compounding ill-defined. In log-odds space, each independent factor adds, which multiplies the odds — the statistically principled way to fuse independent evidence — and `expit` guarantees a valid probability out. This directly implements the compounding behavior the design calls for.*

**Concrete Phase 0 factors (minimum viable set):**

1. **Metallicity ridge (positive, optimum band).** Model [Fe/H] as a function of galactocentric radius: `feh(R) = feh0 - 0.06*(R - R_sun)` with `feh0 ≈ 0.0` at `R_sun ≈ 8.2 kpc`. Map [Fe/H] to an influence in [0,1] that rises from ~0 at very low metallicity (no planets) to ~1 near solar, with a gentle decline at very high metallicity (optional hot-Jupiter penalty). Spatial input: the R grid. Temporal: constant in Phase 0 (or slowly rising if you want cosmic-time enrichment). Backing high (~0.9).
2. **Stellar-density hazard (negative, smooth).** Approximate the disk's stellar density as declining exponentially with R (and |z|): `density(R,z) ∝ exp(-R/h_R) * exp(-|z|/h_z)` with scale lengths `h_R ≈ 2.5 kpc`, `h_z ≈ 0.3 kpc`. Use (normalized) density as the influence: higher density → more supernovae/GRBs/crowding → deeper dip toward the center. Backing moderate (~0.6).
3. **Galactic-center / inner-region penalty (negative).** A steep influence that switches on inside ~2–3 kpc (AGN, extreme crowding). Backing moderate (~0.5).
4. **Individual massive-star hazard (negative, LOCAL-regime, time-evolving).** For the local-zoom demo: influence = a truncated falloff around the star's position (full within a small kill radius, fading outward), multiplied by a `g(t)` that ramps toward the star's collapse time (6.8) and spikes at the supernova. Backing high (~0.9). *This is the factor that demonstrates 4D behavior.*

Provide the spatial helpers, e.g. a truncated inverse-square falloff for point hazards:

```python
def point_falloff(dx, dy, dz, kill_radius_kpc, soft=1e-4):
    d2 = dx*dx + dy*dy + dz*dz
    infl = kill_radius_kpc**2 / (d2 + soft)   # ~1 near source, decays with distance
    return np.clip(infl, 0.0, 1.0) * (np.sqrt(d2) < 5*kill_radius_kpc)  # hard cutoff
```

### 6.7 Grid definition and vectorized field computation (`field.py`)

1. **Galactic-scale grid:** `x = np.linspace(-20, 20, 300)`, `y = np.linspace(-20, 20, 300)`, meshgrid at `z=0`. Precompute `R = np.hypot(X, Y)` once. Evaluate the smooth factors (metallicity, density, inner penalty) on this grid; combine via `habitability_field`.
2. **Local-zoom grid:** a fine meshgrid spanning ~±0.2 kpc around the chosen massive star; evaluate the point-hazard factor (plus a flat baseline from the smooth field) so its dip is resolved.
3. All factor evaluations must be array operations over the meshgrid — no Python loops over cells. *Rationale: a 300×300 grid × several factors × many time steps is only tractable vectorized.*

### 6.8 Temporal model (`field.py` / `factors.py`)

Give each hazard star a main-sequence clock. Approximate main-sequence lifetime:

```python
def ms_lifetime_myr(mass_msun):
    return 1.0e4 * mass_msun**(-2.5)   # ~10 Gyr * (M/Msun)^-2.5, in Myr
```

(A 20 M☉ star → ~5.6 Myr.) Collapse time = `t_birth + ms_lifetime`. Define the hazard temporal profile:

```python
def hazard_g(t, t_birth, t_collapse, decay_myr=2.0):
    if t < t_collapse:
        # ramp: negligible early, approaching 1 near collapse
        return np.clip((t - t_birth) / (t_collapse - t_birth), 0, 1)**3
    else:
        # supernova spike then exponential decay of remnant hazard
        return np.exp(-(t - t_collapse) / decay_myr)
```

The time slider steps `t` across a chosen range (Myr); the field is recomputed per step. *Rationale: this makes the "deepening dip as the star nears collapse, then a burst, then fade" behavior emerge from real stellar-evolution timescales rather than arbitrary animation.*

### 6.9 Static validation rendering (`render.py`, matplotlib)

Before interactivity, render the galactic-scale H field as a 2D heatmap (`imshow`/`pcolormesh`) and a 3D surface (`plot_surface`). Overplot the Sun's position and a few entities. Confirm visually: metallicity ridge present, dip toward center, values in [0,1]. *Rationale: fastest possible feedback loop for debugging the model.*

### 6.10 Interactive rendering (`render.py`, Plotly)

1. **Veil surface:** `plotly.graph_objects.Surface(x=X, y=Y, z=H)` — rotatable/zoomable in-browser.
2. **Entities:** `Scatter3d` markers at entity (x,y,z) with `hovertext` pulling `id/kind/mass/feh` from the entity table — the seed of "click for info."
3. **Time slider:** precompute `H(t)` for a set of time steps; build Plotly frames and a `sliders` control so dragging re-renders the surface at each `t`. For the local-zoom demo, the massive star's dip visibly deepens and then bursts as the slider crosses its collapse time.
4. Output a self-contained HTML file (`fig.write_html(...)`) so it runs in any browser with no server. *Rationale: Plotly gives rotate/zoom/hover/slider from Python; the HTML export makes the deliverable trivially shareable and is a natural stepping-stone to the Phase 1 web app.*

### 6.11 Validation and sanity checks

Assert, and eyeball:

- H is everywhere in [0,1] (log-odds guarantees this; verify no NaNs leak in).
- The **Sun's neighborhood (R ≈ 8.2 kpc) sits in a comparatively favorable band** — not the maximum, but clearly better than the crowded inner few kpc. If it doesn't, the factor weights are miscalibrated.
- Overlapping negatives compound (two nearby hazards produce a deeper dip than either alone) — confirm in the local demo.
- Advancing the time slider monotonically deepens a pre-collapse hazard's dip, then produces the spike-and-decay.
*Rationale: these are the concrete pass/fail signals that the three Phase-0 goals (Section 1) are met.*

---

## 7. Project file structure

```text
veil-phase0/
├── data/
│   ├── raw/              # downloaded CSVs (AT-HYG, exoplanets, hazards)
│   └── processed/        # cached unified entity table (parquet/csv)
├── src/
│   ├── config.py         # constants: R_sun, gradients, grid extents, weights
│   ├── ingest.py         # load + clean + mass/feh estimation → entity table
│   ├── coords.py         # astropy RA/Dec/dist → galactocentric xyz
│   ├── factors.py        # Factor dataclass, factor definitions, profiles
│   ├── field.py          # grids, ms_lifetime, temporal profiles, field eval
│   ├── render.py         # matplotlib validation + plotly interactive/slider
│   └── main.py           # entry point wiring the pipeline + config switches
├── requirements.txt
└── README.md             # how to run, what each module does
```

*Rationale: module boundaries mirror the four concerns (Section 4) so Phase 1 can replace only `render.py` (Python→web) without disturbing the validated model.*

---

## 8. Key module interfaces (contracts for a clean handoff)

- `ingest.load_entities(paths: dict) -> pd.DataFrame` — returns the unified schema (6.5).
- `coords.to_galactocentric(ra, dec, dist_pc) -> (x, y, z)` — vectorized-capable.
- `factors.build_registry(config) -> list[Factor]` — the tunable factor set.
- `field.make_grid(kind: str, config) -> dict` — returns meshgrids + per-factor spatial inputs (e.g., R grid, per-hazard dx/dy/dz grids).
- `field.habitability_field(registry, grids, t, baseline) -> np.ndarray` — H in (0,1).
- `render.static_validate(H, X, Y, entities)` and `render.interactive(frames, entities, out_html)`.

---

## 9. Definition of done (Phase 0 acceptance criteria)

Phase 0 is complete when, from a single `python src/main.py` invocation:

1. Real AT-HYG stars and Exoplanet-Archive planets are ingested and correctly placed in galactocentric coordinates (spot-check: the Sun near R≈8.2 kpc, z≈0).
2. A galactic-scale veil surface renders interactively (rotate/zoom) showing a metallicity-driven favorable annulus and an inner-region dip, with all H ∈ [0,1].
3. Hovering an entity shows its basic info.
4. A time slider drives a local-zoom demo in which a massive star's dip deepens toward its computed collapse time, then spikes and decays.
5. Overlapping factors demonstrably compound (documented in the README with a screenshot).
6. The environment is reproducible from `requirements.txt` and the README explains each module.

---

## 10. Handoff notes to Phase 1 (do not implement now, but design toward)

- **Renderer swap:** `render.py` is the only module Phase 1 replaces — Python/Plotly → a browser app (Three.js/WebGL or deck.gl) consuming the same `field.habitability_field` outputs (precomputed to JSON, or via a small Python API/WebSocket).
- **Keep the field model server-side/portable:** the factor registry and field math should remain the single source of truth; the web layer only visualizes and controls `t`.
- **Provenance channel:** carry the `is_speculative`/`backing` values through to the render so Phase 1 can shade observed vs modeled regions — the honesty feature flagged in the master spec.
- **Scale-out path:** when moving from AT-HYG to Gaia-scale data, introduce out-of-core dataframes (Dask/Vaex) at the ingestion boundary only; nothing else should need to change.
