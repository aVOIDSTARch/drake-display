import numpy as np
from fields.kernels import GaussianKernel
from fields.distance import EuclideanDistance
from fields.source_field import SourceField
from fields.composite_field import CompositeField


def gaussian_source(center):
    return SourceField(
        distance_metric=EuclideanDistance(),
        kernel=GaussianKernel(sigma=1.0),
        center=np.array(center),
        weight=1.0,
    )


def test_composite_is_elementwise_sum_of_sources():
    a = gaussian_source([0.0, 0.0])
    b = gaussian_source([2.0, 0.0])
    points = np.array([[0.0, 0.0], [2.0, 0.0], [1.0, 0.0]])

    result = CompositeField([a, b])(points)

    np.testing.assert_allclose(result, a(points) + b(points))
    # on-source values are symmetric; midpoint gets 2 * exp(-0.5)
    assert result[0] == result[1]
    np.testing.assert_allclose(result[2], 2 * np.exp(-0.5))


def test_empty_composite_is_zero():
    points = np.zeros((5, 2))
    np.testing.assert_array_equal(CompositeField([])(points), np.zeros(5))
