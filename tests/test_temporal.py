import numpy as np
import pytest
from fields.temporal import RampSpikeDecayProfile, StaticProfile, ms_lifetime_myr


def test_ms_lifetime_matches_eq_star_1():
    assert ms_lifetime_myr(1.0) == pytest.approx(1.0e4)
    assert ms_lifetime_myr(20.0) == pytest.approx(5.59, abs=0.01)


def test_static_profile_is_one_with_input_shape():
    np.testing.assert_array_equal(StaticProfile()(np.array([0.0, 5.0, 1e4])), [1.0, 1.0, 1.0])
    assert StaticProfile()(3.0) == 1.0


def test_ramp_rises_monotonically_to_one_at_collapse():
    g = RampSpikeDecayProfile(t_birth_myr=0.0, t_collapse_myr=10.0)
    t = np.linspace(-1.0, 10.0, 50)
    values = g(t)
    assert values[0] == 0.0
    assert np.all(np.diff(values) >= 0)
    assert g(10.0) == 1.0
    assert g(5.0) == pytest.approx(0.125)


def test_decays_after_collapse():
    g = RampSpikeDecayProfile(t_birth_myr=0.0, t_collapse_myr=10.0, decay_myr=2.0)
    assert g(12.0) == pytest.approx(np.exp(-1.0))
    assert g(1e6) == pytest.approx(0.0)


def test_from_mass_sets_collapse_time():
    g = RampSpikeDecayProfile.from_mass(t_birth_myr=100.0, mass_msun=20.0)
    assert g.t_collapse_myr == pytest.approx(100.0 + ms_lifetime_myr(20.0))


@pytest.mark.parametrize("kwargs", [
    dict(t_birth_myr=5.0, t_collapse_myr=5.0),
    dict(t_birth_myr=0.0, t_collapse_myr=1.0, decay_myr=0.0),
])
def test_invalid_clock_rejected(kwargs):
    with pytest.raises(ValueError):
        RampSpikeDecayProfile(**kwargs)
