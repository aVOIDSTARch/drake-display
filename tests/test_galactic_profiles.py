import numpy as np
import pytest
from fields.distance import CylindricalDistance, DiskScaledDistance
from fields.kernels import ExponentialKernel, LogisticStepKernel, MetallicityBandKernel

ORIGIN_3D = np.zeros(3)


def test_cylindrical_distance_ignores_height():
    points = np.array([[3.0, 4.0, 0.0], [3.0, 4.0, 7.0]])
    np.testing.assert_allclose(CylindricalDistance()(points, ORIGIN_3D), [5.0, 5.0])


def test_cylindrical_distance_on_2d_points_is_euclidean():
    np.testing.assert_allclose(CylindricalDistance()(np.array([[3.0, 4.0]]), np.zeros(2)), [5.0])


def test_disk_scaled_distance_with_exponential_is_eq_prof_1():
    metric = DiskScaledDistance(h_R=2.5, h_z=0.3)
    points = np.array([[8.2, 0.0, 0.02], [0.0, 0.0, 0.0]])
    density = ExponentialKernel(scale=1.0)(metric(points, ORIGIN_3D))
    expected = np.exp(-8.2 / 2.5) * np.exp(-0.02 / 0.3)
    np.testing.assert_allclose(density, [expected, 1.0])


def test_logistic_step_is_half_at_radius():
    k = LogisticStepKernel(radius=2.5, width=0.3)
    values = k(np.array([0.0, 2.5, 8.2, 1e6]))
    assert values[0] > 0.99
    assert values[1] == pytest.approx(0.5)
    assert values[2] < 1e-6
    assert np.isfinite(values).all()


def test_metallicity_band_peaks_where_feh_is_optimal():
    k = MetallicityBandKernel()  # feh_opt = solar, so the peak is at R_sun
    assert k(np.array(8.2)) == pytest.approx(1.0)
    assert k.feh(np.array(0.0)) == pytest.approx(0.492)


def test_metallicity_band_falls_faster_on_metal_poor_side():
    k = MetallicityBandKernel()
    inner, outer = k(np.array([8.2 - 5.0, 8.2 + 5.0]))  # same |feh offset| = 0.3
    assert outer < inner < 1.0


def test_point_hazard_full_inside_kill_radius_then_inverse_square_then_cut():
    from fields.kernels import TruncatedInverseSquareKernel
    k = TruncatedInverseSquareKernel(kill_radius=0.01)
    values = k(np.array([0.0, 0.005, 0.01, 0.02, 0.05, 0.0501]))
    np.testing.assert_allclose(values, [1.0, 1.0, 1.0, 0.25, 0.04, 0.0])
