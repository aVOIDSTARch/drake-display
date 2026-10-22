"""
Phase 0 static validation renders (spec section 6.9).

Writes PNGs to output/phase0/:
    galactic.png        -- the whole-disk veil from the smooth factors
    local_t*.png        -- the local-zoom patch around two demo hazard
                           stars at several times, showing the dips
                           deepen toward collapse, then decay

Run from the repo root:  .venv/bin/python scripts/phase0_static.py
"""

from pathlib import Path

from fields.config_loader import load_log_odds_field_from_path
from fields.grid import make_grid
from fields.log_odds_field import LogOddsField
from fields.render import Marker, static_validate

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "output" / "phase0"
SUN = (-8.2, 0.0, 0.0)  # R0 = 8.2 kpc (factors.md Appendix A); Sun on -x, astropy convention
LOCAL_TIMES_MYR = [0.0, 3.0, 5.0, 5.59, 8.0, 11.47, 15.0]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    galactic = load_log_odds_field_from_path(str(REPO / "configs" / "phase0-galactic.toml"))
    hazards = load_log_odds_field_from_path(str(REPO / "configs" / "phase0-local.toml"))

    grid = make_grid("galactic")
    static_validate(galactic(grid.points, t=0.0), grid, "Galactic-scale veil (smooth factors)",
                    str(OUT / "galactic.png"), markers=[Marker(SUN[0], SUN[1], "Sun")])

    local = LogOddsField.combine([galactic, hazards])
    grid = make_grid("local", center=SUN)
    stars = [Marker(f.spatial.center[0], f.spatial.center[1], f.name.split("(")[1].rstrip(")"))
             for f in hazards.factors]
    for t in LOCAL_TIMES_MYR:
        static_validate(local(grid.points, t=t), grid, f"Local zoom around the Sun, t = {t:.2f} Myr",
                        str(OUT / f"local_t{t:05.2f}.png"), markers=stars)

    print(f"wrote {len(LOCAL_TIMES_MYR) + 1} images to {OUT.relative_to(REPO)}/")


if __name__ == "__main__":
    main()
