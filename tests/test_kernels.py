import numpy as np
import pytest
from fields.kernels import (
    CompactSupportKernel,
    ConstantKernel,
    GaussianKernel,
    InverseSquareKernel,
)


def test_compact_support_is_zero_beyond_radius():
    r = np.array([0.0, 0.5, 1.0, 1.5, 10.0])
    np.testing.assert_allclose(CompactSupportKernel(radius=1.0)(r), [1.0, 0.25, 0.0, 0.0, 0.0])


def test_constant_kernel_with_and_without_radius():
    r = np.array([0.0, 1.0, 2.0])
    np.testing.assert_array_equal(ConstantKernel()(r), [1.0, 1.0, 1.0])
    np.testing.assert_array_equal(ConstantKernel(radius=1.0)(r), [1.0, 1.0, 0.0])


def test_inverse_square_is_finite_at_source():
    np.testing.assert_allclose(InverseSquareKernel(scale=2.0)(np.array([0.0, 2.0])), [1.0, 0.5])


@pytest.mark.parametrize("make", [
    lambda: GaussianKernel(sigma=0.0),
    lambda: InverseSquareKernel(scale=-1.0),
    lambda: CompactSupportKernel(radius=0.0),
])
def test_non_positive_parameters_rejected(make):
    with pytest.raises(ValueError):
        make()
