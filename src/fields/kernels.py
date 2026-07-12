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

# add to the bottom of kernels.py

KERNEL_REGISTRY = {
    "gaussian": GaussianKernel,
    "inverse_square": InverseSquareKernel,
    "compact_support": CompactSupportKernel,
    "constant": ConstantKernel,
}
