import pytest

pytest.importorskip("matplotlib")

from fields.grid import GridSpec, make_grid  # noqa: E402
from fields.log_odds_field import LogOddsField  # noqa: E402
from fields.render import Marker, static_validate  # noqa: E402


def test_static_validate_writes_png(tmp_path):
    grid = make_grid("custom", spec=GridSpec(half_width_kpc=1.0, cells=10))
    sample = LogOddsField([], baseline=0.3)(grid.points, t=0.0)
    out = tmp_path / "veil.png"

    static_validate(sample, grid, "smoke", str(out), markers=[Marker(0.0, 0.0, "origin")])

    assert out.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
