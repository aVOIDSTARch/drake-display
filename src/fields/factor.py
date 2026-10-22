"""
factor.py

A Factor is one term of the log-odds habitability sum (factors.md
section 1):

    l_i(points, t) = sign_i * w_i * M_i * f_i(points) * g_i(t)

The spatial profile f_i is anything callable as f(points) -> (...),
normally a SourceField built with weight=1.0 -- the old single
"weight" is split here into sign, backing (w) and magnitude (M) so
that how strong a factor is and how much we trust it stay separate.
"""

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
import numpy as np

from .temporal import StaticProfile, TemporalProfile

# EQ-CORE-4 step 1: confidence assumed for an entity field that
# doesn't declare one. Deliberately low -- unknown is not trusted.
DEFAULT_FIELD_CONFIDENCE = 0.10


@dataclass
class Factor:
    """
    Attributes:
        name: identifier, e.g. "FAC-METAL".
        spatial: f_i, maps points (..., D) -> influence (...) in [0, 1].
        sign: +1 raises habitability, -1 lowers it. Optimum-band ("∩")
            factors are +1 with a band-shaped spatial profile.
        backing: w_i in [0, 1], the science-confidence weight.
        magnitude: M_i >= 0, the tunable base strength.
        temporal: g_i(t), defaults to G-STATIC.
        input_confidences: confidence of each entity field this factor
            reads, e.g. {"feh": 0.5}. Empty means the inputs are
            undeclared and DEFAULT_FIELD_CONFIDENCE is assumed.
    """

    name: str
    spatial: Callable[[np.ndarray], np.ndarray]
    sign: int
    backing: float
    magnitude: float
    temporal: TemporalProfile = field(default_factory=StaticProfile)
    input_confidences: Mapping[str, float] = field(default_factory=dict)

    def __post_init__(self):
        if self.sign not in (1, -1):
            raise ValueError(f"{self.name}: sign must be +1 or -1")
        if not 0.0 <= self.backing <= 1.0:
            raise ValueError(f"{self.name}: backing must be in [0, 1]")
        if self.magnitude < 0:
            raise ValueError(f"{self.name}: magnitude must be non-negative")
        for field_name, c in self.input_confidences.items():
            if not 0.0 <= c <= 1.0:
                raise ValueError(f"{self.name}: confidence of '{field_name}' must be in [0, 1]")

    @property
    def confidence(self) -> float:
        """EQ-CORE-4 steps 1-2: c_i = w_i * min(input confidences)."""
        if self.input_confidences:
            c_input = min(self.input_confidences.values())
        else:
            c_input = DEFAULT_FIELD_CONFIDENCE
        return self.backing * c_input

    def contribution(self, points: np.ndarray, t: float) -> np.ndarray:
        """l_i at each point: shape points.shape[:-1]."""
        strength = self.sign * self.backing * self.magnitude * self.temporal(t)
        return strength * self.spatial(points)
