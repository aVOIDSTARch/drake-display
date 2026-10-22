import numpy as np
import pytest
from fields.grid import GRID_SPECS, GridSpec, make_grid


def test_galactic_grid_matches_spec():
    grid = make_grid("galactic")
    assert grid.points.shape == (300, 300, 3)
    assert grid.extent == (-20.0, 20.0, -20.0, 20.0)
    np.testing.assert_array_equal(grid.points[..., 2], 0.0)


def test_local_grid_is_centered_and_resolves_kill_radius():
    grid = make_grid("local", center=(-8.2, 0.1, 0.02))
    assert grid.points.shape == (200, 200, 3)
    np.testing.assert_allclose(grid.extent, (-8.4, -8.0, -0.1, 0.3))
    np.testing.assert_allclose(grid.points[..., 2], 0.02)
    cell = grid.x[1] - grid.x[0]
    assert cell < 0.010 / 4  # several cells across a 10 pc kill radius


def test_points_line_up_with_meshgrids():
    grid = make_grid("custom", spec=GridSpec(half_width_kpc=1.0, cells=5))
    np.testing.assert_array_equal(grid.points[..., 0], grid.X)
    np.testing.assert_array_equal(grid.points[..., 1], grid.Y)
    assert grid.R[2, 2] == 0.0
    assert grid.R[0, 0] == pytest.approx(np.sqrt(2))


def test_unknown_kind_rejected():
    with pytest.raises(ValueError, match="galactic"):
        make_grid("planetary")


def test_specs_are_the_phase0_values():
    assert GRID_SPECS["galactic"] == GridSpec(20.0, 300)
    assert GRID_SPECS["local"] == GridSpec(0.2, 200)
