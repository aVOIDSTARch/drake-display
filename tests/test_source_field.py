import numpy as np
from fields.kernels import GaussianKernel
from fields.distance import EuclideanDistance
from fields.source_field import SourceField


def make_source(**kwargs):
    defaults = dict(
        distance_metric=EuclideanDistance(),
        kernel=GaussianKernel(sigma=1.0),
        center=np.array([0.0, 0.0]),
        weight=2.0,
    )
    defaults.update(kwargs)
    return SourceField(**defaults)


def test_gaussian_values_scaled_by_weight():
    points = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 2.0]])
    result = make_source()(points)
    np.testing.assert_allclose(result, 2.0 * np.exp([0.0, -0.5, -2.0]))


def test_preserves_leading_grid_shape():
    X, Y = np.meshgrid(np.linspace(-1, 1, 4), np.linspace(-1, 1, 3))
    points = np.stack([X, Y], axis=-1)  # (3, 4, 2)
    assert make_source()(points).shape == (3, 4)


def test_unnamed_sources_get_distinct_names():
    a = make_source()
    b = make_source()
    assert a.name.startswith("unnamed_factor_")
    assert a.name != b.name
