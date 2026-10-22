"""
Phase 0 sanity checks (plan-phase0-veil-prototype.md section 6.11),
run against the real configs in configs/.
"""

from pathlib import Path

import numpy as np
import pytest
from fields.config_loader import load_log_odds_field_from_path
from fields.grid import make_grid
from fields.log_odds_field import LogOddsField

CONFIGS = Path(__file__).parent.parent / "configs"
SUN = (-8.2, 0.0, 0.0)
R_SUN = 8.2


@pytest.fixture(scope="module")
def galactic():
    return load_log_odds_field_from_path(str(CONFIGS / "phase0-galactic.toml"))


@pytest.fixture(scope="module")
def hazards():
    return load_log_odds_field_from_path(str(CONFIGS / "phase0-local.toml"))


@pytest.fixture(scope="module")
def galactic_sample(galactic):
    grid = make_grid("galactic")
    return grid, galactic(grid.points, t=0.0)


def test_veil_is_a_valid_probability_everywhere(galactic_sample):
    _, sample = galactic_sample
    for values in (sample.height, sample.confidence):
        assert np.isfinite(values).all()
        assert np.all((values >= 0.0) & (values <= 1.0))


def test_solar_band_clearly_beats_inner_region(galactic_sample):
    grid, sample = galactic_sample
    solar_band = sample.height[np.abs(grid.R - R_SUN) < 0.5].mean()
    inner = sample.height[grid.R < 3.0].mean()
    assert solar_band > inner + 0.25  # calibrated: ~0.75 vs ~0.42 (ADR-013)


def test_local_veil_is_a_valid_probability_at_all_times(galactic, hazards):
    local = LogOddsField.combine([galactic, hazards])
    grid = make_grid("local", center=SUN)
    for t in np.linspace(0.0, 20.0, 9):
        height = local(grid.points, t=t).height
        assert np.isfinite(height).all()
        assert np.all((height >= 0.0) & (height <= 1.0))


def test_overlapping_hazards_compound(galactic, hazards):
    star_a, star_b = hazards.factors
    midpoint = ((star_a.spatial.center + star_b.spatial.center) / 2)[np.newaxis, :]
    t = 5.0  # both stars on their pre-collapse ramp

    def height_with(*stars):
        return LogOddsField.combine([galactic, LogOddsField(list(stars))])(midpoint, t).height[0]

    both = height_with(star_a, star_b)
    assert both < height_with(star_a)
    assert both < height_with(star_b)


def test_pre_collapse_dip_deepens_then_spikes_and_decays(galactic, hazards):
    star_a = hazards.factors[0]
    local = LogOddsField.combine([galactic, hazards])
    at_star = star_a.spatial.center[np.newaxis, :]
    t_collapse = star_a.temporal.t_collapse_myr

    def height(t):
        return local(at_star, t).height[0]

    before = [height(t) for t in np.linspace(0.0, t_collapse - 1e-6, 40)]
    after = [height(t) for t in np.linspace(t_collapse, t_collapse + 10.0, 40)]

    assert np.all(np.diff(before) <= 0), "dip should deepen monotonically toward collapse"
    assert np.all(np.diff(after) >= 0), "dip should recover monotonically after the supernova"
    assert height(t_collapse) == pytest.approx(min(before + after))
    assert height(t_collapse) < 0.15  # calibrated kill zone, not a cosmetic dip (ADR-013)
