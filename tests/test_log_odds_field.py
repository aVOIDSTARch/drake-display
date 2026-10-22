import numpy as np
import pytest
from fields.distance import EuclideanDistance
from fields.factor import Factor
from fields.kernels import CompactSupportKernel, GaussianKernel
from fields.log_odds_field import NO_CONTRIBUTION_CONFIDENCE, LogOddsField, logistic
from fields.source_field import SourceField


def hazard(center, magnitude=3.0, confidence=1.0, backing=0.9):
    spatial = SourceField(EuclideanDistance(), GaussianKernel(sigma=1.0), center=np.array(center))
    return Factor(f"hazard_{center}", spatial, sign=-1, backing=backing, magnitude=magnitude,
                  input_confidences={"position": confidence})


def test_logistic_is_stable_at_extremes():
    values = logistic(np.array([-1e4, 0.0, 1e4]))
    np.testing.assert_allclose(values, [0.0, 0.5, 1.0])


def test_no_factors_gives_baseline_probability():
    sample = LogOddsField([], baseline=1.0)(np.zeros((4, 2)), t=0.0)
    np.testing.assert_allclose(sample.height, logistic(1.0))
    np.testing.assert_array_equal(sample.confidence, NO_CONTRIBUTION_CONFIDENCE)


def test_height_stays_in_unit_interval_under_extreme_stacking():
    factors = [hazard([0.0, 0.0], magnitude=1e3) for _ in range(5)]
    sample = LogOddsField(factors)(np.array([[0.0, 0.0], [50.0, 0.0]]), t=0.0)
    assert np.all((sample.height >= 0) & (sample.height <= 1))
    assert np.isfinite(sample.height).all()


def test_overlapping_hazards_compound():
    point = np.array([[1.0, 0.0]])  # between the two hazards
    a, b = hazard([0.0, 0.0]), hazard([2.0, 0.0])
    alone_a = LogOddsField([a])(point, t=0.0).height
    alone_b = LogOddsField([b])(point, t=0.0).height
    together = LogOddsField([a, b])(point, t=0.0).height
    assert together < min(alone_a, alone_b)


def test_logit_is_baseline_plus_contributions():
    a, b = hazard([0.0, 0.0]), hazard([2.0, 0.0])
    points = np.array([[0.5, 0.5], [3.0, 1.0]])
    sample = LogOddsField([a, b], baseline=0.7)(points, t=0.0)
    np.testing.assert_allclose(
        sample.logit, 0.7 + a.contribution(points, 0.0) + b.contribution(points, 0.0)
    )


def test_single_factor_confidence_is_its_own():
    factor = hazard([0.0, 0.0], confidence=0.5, backing=0.8)
    sample = LogOddsField([factor])(np.array([[0.0, 0.0], [1.0, 1.0]]), t=0.0)
    np.testing.assert_allclose(sample.confidence, factor.confidence)


def test_confidence_is_magnitude_weighted_mean():
    trusted = hazard([0.0, 0.0], confidence=1.0, backing=1.0)
    shaky = hazard([4.0, 0.0], confidence=0.1, backing=1.0)
    points = np.array([[0.0, 0.0], [2.0, 0.0], [4.0, 0.0]])
    confidence = LogOddsField([trusted, shaky])(points, t=0.0).confidence
    assert confidence[0] > confidence[1] > confidence[2]
    assert confidence[1] == pytest.approx(0.55)  # equidistant: equal |l|, plain mean


def test_confidence_falls_back_where_nothing_contributes():
    spatial = SourceField(EuclideanDistance(), CompactSupportKernel(radius=1.0), center=np.zeros(2))
    factor = Factor("local", spatial, sign=-1, backing=1.0, magnitude=1.0,
                    input_confidences={"position": 1.0})
    sample = LogOddsField([factor])(np.array([[0.0, 0.0], [5.0, 0.0]]), t=0.0)
    np.testing.assert_allclose(sample.confidence, [1.0, NO_CONTRIBUTION_CONFIDENCE])


def test_combine_adds_factors_and_baselines():
    a, b = hazard([0.0, 0.0]), hazard([2.0, 0.0])
    combined = LogOddsField.combine([LogOddsField([a], baseline=0.5), LogOddsField([b], baseline=0.25)])
    points = np.array([[1.0, 0.0], [5.0, 5.0]])
    np.testing.assert_allclose(
        combined(points, t=0.0).logit,
        LogOddsField([a, b], baseline=0.75)(points, t=0.0).logit,
    )
