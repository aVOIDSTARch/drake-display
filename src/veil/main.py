"""
main.py

Phase 0 single entry point (plan-phase0 section 9):

    python src/main.py            # or: python -m veil
    python src/main.py --view local --t-end 20 --t-step 0.5

Fetches any missing raw catalog, ingests the unified entity table,
spot-checks the coordinate frame, builds the factor registry, then
writes static PNGs and the interactive HTML page to output/phase0/.
"""

import argparse
from pathlib import Path

import numpy as np

from fields.grid import GridSpec, make_grid
from fields.render import Marker, static_validate

from . import interactive
from .coords import R0_KPC
from .fetch import EXOPLANET_FILE, HYG_FILE, OB_FILE, WR_FILE, fetch_missing
from .ingest import load_entities
from .registry import HAZARD_KINDS, build_fields, hazards_reaching, near

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "data" / "raw"
PROCESSED = REPO / "data" / "processed"
CONFIGS = REPO / "configs"
SUN_ID = "hyg:0"

# Interactive grids are coarser than the static GRID_SPECS to keep the HTML small;
# 150 cells over +/-0.25 kpc is still ~3 pc per cell against a 10 pc kill radius.
GALACTIC_HTML_SPEC = GridSpec(half_width_kpc=20.0, cells=200)
LOCAL_HTML_SPEC = GridSpec(half_width_kpc=0.25, cells=150)


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render the Phase 0 habitability veil.")
    parser.add_argument("--view", choices=["galactic", "local", "both"], default="both")
    parser.add_argument("--t-end", type=float, default=15.0, help="last slider time, Myr from now")
    parser.add_argument("--t-step", type=float, default=0.5, help="slider step, Myr")
    parser.add_argument("--out", type=Path, default=REPO / "output" / "phase0")
    parser.add_argument("--no-fetch", action="store_true", help="fail instead of downloading missing data")
    parser.add_argument("--project-hazards", action="store_true",
                        help="measure hazard reach in the plane only, so off-plane stars also dip "
                             "(overstates their reach; default is a true 3D slice)")
    return parser.parse_args(argv)


def check_sun(entities) -> np.ndarray:
    """Acceptance spot-check: the Sun near R ~ 8.2 kpc, z ~ 0."""
    sun = entities.loc[entities["id"] == SUN_ID].iloc[0]
    position = sun[["x_gal_kpc", "y_gal_kpc", "z_gal_kpc"]].to_numpy(dtype=float)
    if abs(sun["r_gal_kpc"] - R0_KPC) > 0.1 or abs(sun["z_gal_kpc"]) > 0.05:
        raise RuntimeError(f"coordinate frame is off: Sun at R={sun['r_gal_kpc']:.3f}, z={sun['z_gal_kpc']:.3f} kpc")
    print(f"Sun at x={position[0]:.3f} y={position[1]:.3f} z={position[2]:.3f} kpc (R={sun['r_gal_kpc']:.3f})")
    return position


def main(argv=None) -> None:
    args = parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)

    if args.no_fetch:
        missing = [f for f in (HYG_FILE, EXOPLANET_FILE, WR_FILE, OB_FILE) if not (RAW / f).exists()]
        if missing:
            raise SystemExit(f"missing raw data {missing}; run without --no-fetch to download")
    else:
        fetch_missing(RAW)

    entities = load_entities({
        "hyg": RAW / HYG_FILE,
        "exoplanets": RAW / EXOPLANET_FILE,
        "hazards": REPO / "data" / "curated" / "phase0_hazard_stars.csv",
        "wolf_rayet": RAW / WR_FILE,
        "ob_stars": RAW / OB_FILE,
    })
    PROCESSED.mkdir(parents=True, exist_ok=True)
    entities.to_csv(PROCESSED / "entities.csv", index=False)
    print(f"{len(entities)} entities -> {(PROCESSED / 'entities.csv').relative_to(REPO)}")
    print(entities["kind"].value_counts().to_string())

    sun = check_sun(entities)
    galactic, local = build_fields(entities, CONFIGS, project_hazards=args.project_hazards,
                                   local_patch=(sun, LOCAL_HTML_SPEC.half_width_kpc))
    print(f"registry: {len(galactic.factors)} galactic factors, "
          f"{len(local.factors) - len(galactic.factors)} point hazards reach the local view")

    sun_rows = entities[entities["id"] == SUN_ID]
    hazards = entities[entities["kind"].isin(HAZARD_KINDS)]
    systems = entities[entities["kind"] == "planetary_system"]
    stars = entities[entities["kind"].isin(interactive.STAR_CLOUD_STYLES) & (entities["id"] != SUN_ID)]
    figures = []

    if args.view in ("galactic", "both"):
        grid = make_grid("galactic")
        static_validate(galactic(grid.points, t=0.0), grid, "Galactic-scale veil",
                        str(args.out / "galactic.png"), markers=[Marker(sun[0], sun[1], "Sun")])
        grid = make_grid("galactic", spec=GALACTIC_HTML_SPEC)
        figures.append(interactive.galactic_figure(
            galactic, grid, {"system": systems, "hazard": hazards, "sun": sun_rows},
            clouds=interactive.star_clouds(stars, galactic, t=0.0)))

    if args.view in ("local", "both"):
        grid = make_grid("local", center=sun, spec=LOCAL_HTML_SPEC)
        hw = LOCAL_HTML_SPEC.half_width_kpc
        animated = {"hazard": near(hazards, sun, hw), "sun": sun_rows}
        static = {"system": near(systems, sun, hw)}
        times = np.round(np.arange(0.0, args.t_end + args.t_step / 2, args.t_step), 6)
        static_validate(local(grid.points, t=0.0), grid, "Local zoom around the Sun, t = 0",
                        str(args.out / "local_now.png"),
                        markers=[Marker(r.x_gal_kpc, r.y_gal_kpc, r.name) for r in
                                 hazards_reaching(entities, sun, hw, args.project_hazards).itertuples()])
        local_stars = near(stars, sun, hw)
        figures.append(interactive.local_figure(local, grid, animated, static, times,
                                                projected=args.project_hazards,
                                                clouds=interactive.star_clouds(local_stars, local, times[0])))
        print(f"local view: {len(animated['hazard'])} hazards, {len(static['system'])} exoplanet systems, "
              f"{len(local_stars):,} stars, {len(times)} time steps")

    html = args.out / "veil.html"
    interactive.write_html(figures, html, projected=args.project_hazards)
    print(f"wrote {html.relative_to(REPO) if html.is_relative_to(REPO) else html} "
          f"({html.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
