"""
distance.py

Defines the DistanceMetric contract: given an array of points and a
single center point, return an array of scalar distances (one per
point). Like Kernel, this stays dimension-agnostic -- it works on
2D or 3D points identically, because the coordinate axis is just
"the last axis" of whatever array you hand it.
"""

from abc import ABC, abstractmethod
import numpy as np


class DistanceMetric(ABC):
    """
    Contract: distance(points, center) takes an array of shape
    (..., D) -- any number of leading dimensions, D coordinates
    per point -- and a center of shape (D,), returning an array
    of shape (...) : one scalar distance per point, coordinate
    axis consumed.
    """

    @abstractmethod
    def distance(self, points: np.ndarray, center: np.ndarray) -> np.ndarray:
        ...

    def __call__(self, points: np.ndarray, center: np.ndarray) -> np.ndarray:
        return self.distance(points, center)


class EuclideanDistance(DistanceMetric):
    """
    Standard straight-line distance. Produces circular (2D) or
    spherical (3D+) effect regions when paired with any kernel.
    """

    def distance(self, points: np.ndarray, center: np.ndarray) -> np.ndarray:
        diff = points - center          # broadcasts center across all points
        return np.sqrt(np.sum(diff ** 2, axis=-1))


class AnisotropicDistance(DistanceMetric):
    """
    Mahalanobis-style distance: d(p,c) = sqrt((p-c)^T A (p-c))

    A is a symmetric positive-definite matrix encoding scale and
    rotation. A diagonal A with unequal entries stretches the
    circle into an axis-aligned ellipse; off-diagonal entries
    rotate it. This is what turns "circle" into "ellipse at
    any angle."
    """

    def __init__(self, A: np.ndarray):
        self.A = np.asarray(A, dtype=float)

    def distance(self, points: np.ndarray, center: np.ndarray) -> np.ndarray:
        diff = points - center                      # shape (..., D)
        # einsum contracts diff against A against diff, per point,
        # without an explicit Python loop over the leading dims.
        quad_form = np.einsum('...i,ij,...j->...', diff, self.A, diff)
        return np.sqrt(quad_form)
