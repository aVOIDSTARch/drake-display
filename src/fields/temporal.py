"""
temporal.py

Defines the TemporalProfile contract: g(t), a factor's strength as a
function of time, in [0, 1]. Like Kernel, profiles are pure numpy
transforms -- t may be a scalar or an array of times, and the result
has the same shape. Times are in Myr throughout.

Profiles here implement the temporal half of the shared profile
library in factors.md section 3 (G-STATIC, G-RAMP-SPIKE-DECAY).
"""

from abc import ABC, abstractmethod
import numpy as np

# EQ-STAR-1 normalization: t_MS ~ 1e4 Myr * (M / Msun)^-2.5
MS_LIFETIME_NORM_MYR = 1.0e4


def ms_lifetime_myr(mass_msun: float) -> float:
    """Main-sequence lifetime from EQ-STAR-1 (Approximate).
    A 20 Msun star gives ~5.6 Myr."""
    if mass_msun <= 0:
        raise ValueError("mass_msun must be positive")
    return MS_LIFETIME_NORM_MYR * mass_msun ** -2.5


class TemporalProfile(ABC):
    """
    Contract: evaluate(t) takes a scalar or array of times (Myr) and
    returns a same-shape array of strengths in [0, 1].
    """

    @abstractmethod
    def evaluate(self, t: np.ndarray | float) -> np.ndarray:
        ...

    def __call__(self, t: np.ndarray | float) -> np.ndarray:
        return self.evaluate(t)


class StaticProfile(TemporalProfile):
    """
    G-STATIC: g(t) = 1 for all t. The default for galactic-smooth
    factors in Phase 0 (G-ENRICH is also held here until EQ-CHEM-4
    exists).
    """

    def evaluate(self, t: np.ndarray | float) -> np.ndarray:
        return np.ones_like(np.asarray(t, dtype=float))


class RampSpikeDecayProfile(TemporalProfile):
    """
    G-RAMP-SPIKE-DECAY: the hazard clock for a massive star.

        t <  t_collapse:  ((t - t_birth) / (t_collapse - t_birth))^3, clipped to [0, 1]
        t >= t_collapse:  exp(-(t - t_collapse) / decay_myr)

    Negligible early, approaching 1 near collapse (EQ-PROF-3), peaking
    at 1 at the supernova, then decaying as the remnant hazard fades
    (EQ-PROF-4).
    """

    def __init__(self, t_birth_myr: float, t_collapse_myr: float, decay_myr: float = 2.0):
        if t_collapse_myr <= t_birth_myr:
            raise ValueError("t_collapse_myr must be after t_birth_myr")
        if decay_myr <= 0:
            raise ValueError("decay_myr must be positive")
        self.t_birth_myr = t_birth_myr
        self.t_collapse_myr = t_collapse_myr
        self.decay_myr = decay_myr

    @classmethod
    def from_mass(cls, t_birth_myr: float, mass_msun: float,
                  decay_myr: float = 2.0) -> "RampSpikeDecayProfile":
        """Collapse time = birth + main-sequence lifetime (EQ-STAR-1)."""
        return cls(t_birth_myr, t_birth_myr + ms_lifetime_myr(mass_msun), decay_myr)

    def evaluate(self, t: np.ndarray | float) -> np.ndarray:
        t = np.asarray(t, dtype=float)
        span = self.t_collapse_myr - self.t_birth_myr
        ramp = np.clip((t - self.t_birth_myr) / span, 0.0, 1.0) ** 3
        # maximum() keeps the unused branch of where() from overflowing
        decay = np.exp(-np.maximum(t - self.t_collapse_myr, 0.0) / self.decay_myr)
        return np.where(t < self.t_collapse_myr, ramp, decay)


TEMPORAL_REGISTRY = {
    "static": StaticProfile,
    "ramp_spike_decay": RampSpikeDecayProfile,
}
