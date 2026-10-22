"""
Calibration targets (DECISIONS.md ADR-013), checked against the shipped
configs/phase0-galactic.toml and the FAC-SN constants in veil.registry.
"""

from pathlib import Path

import numpy as np
import pytest
from fields.config_loader import load_log_odds_field_from_path
from fields.log_odds_field import LogOddsField

CONFIGS = Path(__file__).parent.parent / "configs"
TOLERANCE = 0.03


@pytest.fixture(scope="module")
def galactic():
    return load_log_odds_field_from_path(str(CONFIGS / "phase0-galactic.toml"))


def height_at_radius(field, R, t=0.0):
    R = np.atleast_1d(np.asarray(R, dtype=float))
    points = np.stack([-R, np.zeros_like(R), np.zeros_like(R)], axis=-1)  # along the Sun's direction
    return field(points, t).height


@pytest.mark.parametrize("R,target", [(0.0, 0.20), (8.2, 0.75), (20.0, 0.40)])
def test_galactic_targets(galactic, R, target):
    assert height_at_radius(galactic, R)[0] == pytest.approx(target, abs=TOLERANCE)


def test_rises_monotonically_from_center_to_sun(galactic):
    assert np.all(np.diff(height_at_radius(galactic, np.linspace(0.0, 8.2, 83))) > 0)


def test_solar_band_is_the_peak(galactic):
    R = np.linspace(0.0, 20.0, 201)
    assert R[np.argmax(height_at_radius(galactic, R))] == pytest.approx(8.2, abs=0.5)


def test_supernova_at_collapse_reaches_kill_target(galactic):
    pd = pytest.importorskip("pandas")
    from veil.registry import supernova_factor

    star = pd.Series({
        "name": "test progenitor", "x_gal_kpc": -8.2, "y_gal_kpc": 0.0, "z_gal_kpc": 0.0,
        "t_birth_myr": -5.0, "t_collapse_myr": 0.0,
        "x_gal_kpc__conf": 0.85, "mass_msun__conf": 0.3, "t_collapse_myr__conf": 0.1,
    })
    local = LogOddsField.combine([galactic, LogOddsField([supernova_factor(star)])])
    at_star = np.array([[-8.2, 0.0, 0.0]])
    assert local(at_star, t=0.0).height[0] <= 0.10
    # well before the ramp, the star leaves the solar background untouched
    assert local(at_star, t=-5.0).height[0] == pytest.approx(0.75, abs=TOLERANCE)
