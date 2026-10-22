import numpy as np
import pytest
from fields.distance import EuclideanDistance
from fields.factor import DEFAULT_FIELD_CONFIDENCE, Factor
from fields.kernels import GaussianKernel
from fields.source_field import SourceField
from fields.temporal import RampSpikeDecayProfile


def gaussian_spatial():
    return SourceField(EuclideanDistance(), GaussianKernel(sigma=1.0), center=np.zeros(2))


def test_contribution_is_sign_backing_magnitude_spatial_temporal():
    factor = Factor("hazard", gaussian_spatial(), sign=-1, backing=0.5, magnitude=2.0,
                    temporal=RampSpikeDecayProfile(0.0, 10.0))
    points = np.array([[0.0, 0.0], [1.0, 0.0]])
    expected = -1 * 0.5 * 2.0 * np.exp([0.0, -0.5]) * 0.125
    np.testing.assert_allclose(factor.contribution(points, t=5.0), expected)


def test_confidence_is_backing_times_weakest_input():
    factor = Factor("f", gaussian_spatial(), sign=1, backing=0.8, magnitude=1.0,
                    input_confidences={"r_gal_kpc": 0.9, "feh": 0.5})
    assert factor.confidence == pytest.approx(0.4)


def test_undeclared_inputs_assume_default_confidence():
    factor = Factor("f", gaussian_spatial(), sign=1, backing=0.8, magnitude=1.0)
    assert factor.confidence == pytest.approx(0.8 * DEFAULT_FIELD_CONFIDENCE)


@pytest.mark.parametrize("kwargs", [
    dict(sign=0, backing=0.5, magnitude=1.0),
    dict(sign=1, backing=1.5, magnitude=1.0),
    dict(sign=1, backing=0.5, magnitude=-1.0),
    dict(sign=1, backing=0.5, magnitude=1.0, input_confidences={"feh": 2.0}),
])
def test_invalid_factor_rejected(kwargs):
    with pytest.raises(ValueError):
        Factor("bad", gaussian_spatial(), **kwargs)
