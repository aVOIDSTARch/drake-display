"""
Defines the Kernel contract: a pointwise, dimension-agnostic transform
from distance -> falloff weight. Kernels know nothing about geometry,
centers, or the space being sampled -- they only transform whatever
numpy array of distances they're handed. This is what makes them
reusable across 0D/1D/2D/3D+ without any dimensionality-aware code here.
"""

from abc import ABC, abstractmethod
import numpy as np


class Kernel(ABC):
    """Abstract base for all falloff kernels.

    Contract: evaluate(r) takes a numpy array (any shape) of
    non-negative distances and returns a same-shape array of
    falloff weights. Because it's built from numpy ufuncs, it
    works unmodified whether r is a single point, a line, a
    grid, or a volume.
    """

    @abstractmethod
    def evaluate(self, r: np.ndarray) -> np.ndarray:
        ...

    def __call__(self, r: np.ndarray) -> np.ndarray:
        # Lets a Kernel instance be used like a function: kernel(r)
        # instead of kernel.evaluate(r). Purely a convenience.
        return self.evaluate(r)

class ConstantKernel(Kernel):
    """
    kappa(r) = 1 everywhere (or 0 beyond an optional radius).

    The identity/degenerate case discussed earlier: proves the
    abstraction holds even when distance is irrelevant.
    """

    def __init__(self, radius: float | None = None):
        # radius=None -> infinite support (uniform everywhere)
        # radius=R    -> hard cutoff, a "disk" indicator kernel
        self.radius = radius

    def evaluate(self, r: np.ndarray) -> np.ndarray:
        if self.radius is None:
            return np.ones_like(r, dtype=float)
        return np.where(r <= self.radius, 1.0, 0.0)

class GaussianKernel(Kernel):
    """
    kappa(r) = exp(-r^2 / (2 * sigma^2))

    Smooth, no singularity at r=0, effectively zero far away
    without a hard edge. This should be your default choice
    unless you have a specific reason for another kernel.
    """

    def __init__(self, sigma: float):
        if sigma <= 0:
            raise ValueError("sigma must be positive")
        self.sigma = sigma

    def evaluate(self, r: np.ndarray) -> np.ndarray:
        return np.exp(-(r ** 2) / (2 * self.sigma ** 2))

class InverseSquareKernel(Kernel):
    """
    kappa(r) = 1 / (1 + (r / scale)^2)

    True gravity-like falloff. The "+1" avoids a divide-by-zero
    blowup exactly at the source -- without it, r=0 gives an
    undefined infinite spike, which is rarely what you want in
    a rendered field.
    """

    def __init__(self, scale: float = 1.0):
        if scale <= 0:
            raise ValueError("scale must be positive")
        self.scale = scale

    def evaluate(self, r: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + (r / self.scale) ** 2)

class CompactSupportKernel(Kernel):
    """
    kappa(r) = max(0, 1 - r/R)^2   for r <= R, else 0.

    Effect hits exactly zero beyond radius R. This is what lets
    you later spatially index sources and skip evaluating ones
    that are too far from a given point to matter -- a real
    performance win once you have many sources over a large grid.
    """

    def __init__(self, radius: float):
        if radius <= 0:
            raise ValueError("radius must be positive")
        self.radius = radius

    def evaluate(self, r: np.ndarray) -> np.ndarray:
        normalized = np.clip(1.0 - (r / self.radius), a_min=0.0, a_max=None)
        return normalized ** 2

class ExponentialKernel(Kernel):
    """
    kappa(r) = exp(-r / scale)

    Paired with DiskScaledDistance this is the double-exponential
    disk density of EQ-PROF-1 (P-DISKDENS), normalized to 1 at the
    galactic center.
    """

    def __init__(self, scale: float = 1.0):
        if scale <= 0:
            raise ValueError("scale must be positive")
        self.scale = scale

    def evaluate(self, r: np.ndarray) -> np.ndarray:
        return np.exp(-r / self.scale)

class LogisticStepKernel(Kernel):
    """
    kappa(r) = 1 / (1 + exp((r - radius) / width))

    A smooth step: ~1 inside radius, exactly 0.5 at radius, ~0
    outside. width sets how sharp the edge is. This is P-INNER,
    the inner-region penalty switching on inside R_inner.
    """

    def __init__(self, radius: float, width: float):
        if radius <= 0:
            raise ValueError("radius must be positive")
        if width <= 0:
            raise ValueError("width must be positive")
        self.radius = radius
        self.width = width

    def evaluate(self, r: np.ndarray) -> np.ndarray:
        # 0.5 * (1 - tanh(x/2)) == 1 / (1 + e^x), without overflow for large x
        return 0.5 * (1.0 - np.tanh((r - self.radius) / (2 * self.width)))

class MetallicityBandKernel(Kernel):
    """
    P-RADIAL for FAC-METAL: galactocentric radius -> [Fe/H] -> influence.

    Step one, EQ-CHEM-1 (Established):
        feh(R) = feh_sun + gradient * (R - r_sun_kpc)
    Step two, the optimum band (EQ-CHEM-3, PLACEHOLDER -- the real
    curve is a known gap): an asymmetric Gaussian in [Fe/H] peaking
    at 1 at feh_opt, falling steeply below (too few metals for
    planets) and gently above (hot-Jupiter penalty).

    Expects r to be galactocentric cylindrical radius in kpc, i.e.
    pair with CylindricalDistance centered on the galactic center.
    """

    def __init__(self, r_sun_kpc: float = 8.2, feh_sun: float = 0.0,
                 gradient: float = -0.06, feh_opt: float = 0.0,
                 sigma_low: float = 0.3, sigma_high: float = 0.6):
        if sigma_low <= 0 or sigma_high <= 0:
            raise ValueError("sigma_low and sigma_high must be positive")
        self.r_sun_kpc = r_sun_kpc
        self.feh_sun = feh_sun
        self.gradient = gradient
        self.feh_opt = feh_opt
        self.sigma_low = sigma_low
        self.sigma_high = sigma_high

    def feh(self, r: np.ndarray) -> np.ndarray:
        return self.feh_sun + self.gradient * (np.asarray(r, dtype=float) - self.r_sun_kpc)

    def evaluate(self, r: np.ndarray) -> np.ndarray:
        offset = self.feh(r) - self.feh_opt
        sigma = np.where(offset < 0, self.sigma_low, self.sigma_high)
        return np.exp(-(offset ** 2) / (2 * sigma ** 2))


class TruncatedInverseSquareKernel(Kernel):
    """
    P-POINT (EQ-PROF-2): kappa(r) = min(1, (kill_radius / r)^2),
    and exactly 0 beyond cutoff_factor * kill_radius.

    Full strength inside the kill radius, inverse-square fade
    outside it, hard edge so a point hazard only touches nearby
    cells. Note the edge is a step: at the default cutoff the
    falloff has only reached 1/25.
    """

    def __init__(self, kill_radius: float, cutoff_factor: float = 5.0):
        if kill_radius <= 0:
            raise ValueError("kill_radius must be positive")
        if cutoff_factor < 1:
            raise ValueError("cutoff_factor must be at least 1")
        self.kill_radius = kill_radius
        self.cutoff_factor = cutoff_factor

    def evaluate(self, r: np.ndarray) -> np.ndarray:
        r = np.asarray(r, dtype=float)
        # max() keeps r >= kill_radius in the ratio, so r = 0 never divides by zero
        falloff = (self.kill_radius / np.maximum(r, self.kill_radius)) ** 2
        return np.where(r <= self.cutoff_factor * self.kill_radius, falloff, 0.0)


KERNEL_REGISTRY = {
    "truncated_inverse_square": TruncatedInverseSquareKernel,
    "gaussian": GaussianKernel,
    "inverse_square": InverseSquareKernel,
    "compact_support": CompactSupportKernel,
    "constant": ConstantKernel,
    "exponential": ExponentialKernel,
    "logistic_step": LogisticStepKernel,
    "metallicity_band": MetallicityBandKernel,
}
