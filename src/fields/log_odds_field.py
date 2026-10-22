"""
log_odds_field.py

The log-odds counterpart of CompositeField. Where CompositeField sums
raw contributions, LogOddsField sums Factor contributions in log-odds
space and maps the total through the logistic, so overlapping factors
compound without ever leaving [0, 1]:

    logit(H) = B0 + sum_i l_i          (EQ-CORE-1)
    H = 1 / (1 + exp(-logit(H)))       (EQ-CORE-2)

The same pass also produces the confidence channel (EQ-CORE-4):

    confidence_here = sum_i c_i * |l_i| / sum_i |l_i|
"""

from dataclasses import dataclass
import numpy as np

from .factor import Factor

# EQ-CORE-4: confidence where no factor contributes at all. The spec
# says "treat as low/baseline"; with nothing to go on, trust nothing.
NO_CONTRIBUTION_CONFIDENCE = 0.0


def logistic(x: np.ndarray) -> np.ndarray:
    """Numerically stable 1 / (1 + e^-x); no overflow at large |x|."""
    return 0.5 * (1.0 + np.tanh(0.5 * np.asarray(x, dtype=float)))


@dataclass
class VeilSample:
    """One evaluation of the veil. All arrays share points.shape[:-1]."""
    height: np.ndarray      # H in [0, 1] -- the surface
    confidence: np.ndarray  # confidence_here in [0, 1] -- the hue
    logit: np.ndarray       # B0 + sum of contributions, before the logistic


class LogOddsField:
    """
    Attributes:
        factors: the Factor terms of the sum.
        baseline: B0, the log-odds with no factors present.
    """

    def __init__(self, factors: list[Factor], baseline: float = 0.0):
        self.factors = factors
        self.baseline = baseline

    @classmethod
    def combine(cls, fields: list["LogOddsField"]) -> "LogOddsField":
        """One field whose logit is the sum of the inputs' logits: all
        factors together, baselines added. E.g. the galactic smooth
        field plus a local set of point hazards."""
        factors = [factor for f in fields for factor in f.factors]
        return cls(factors, baseline=sum(f.baseline for f in fields))

    def __call__(self, points: np.ndarray, t: float) -> VeilSample:
        return self.evaluate(points, t)

    def evaluate(self, points: np.ndarray, t: float) -> VeilSample:
        """
        Evaluate the veil at points (..., D) and time t (Myr).
        """
        shape = points.shape[:-1]
        logit = np.full(shape, self.baseline, dtype=float)
        weighted_confidence = np.zeros(shape)
        total_magnitude = np.zeros(shape)

        for factor in self.factors:
            contribution = factor.contribution(points, t)
            logit += contribution
            weighted_confidence += factor.confidence * np.abs(contribution)
            total_magnitude += np.abs(contribution)

        has_contribution = total_magnitude > 0
        confidence = np.divide(
            weighted_confidence, total_magnitude,
            out=np.full(shape, NO_CONTRIBUTION_CONFIDENCE),
            where=has_contribution,
        )
        return VeilSample(height=logistic(logit), confidence=confidence, logit=logit)
