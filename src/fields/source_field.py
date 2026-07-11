from . import distance
from . import kernels
import numpy as np

_unnamed_counter = 0

class SourceField():
    """
    A SourceField is a combination of a distance metric and a kernel.
    It defines how to compute the influence of a source point on
    surrounding points in space.

    Attributes:
        distance_metric: An instance of DistanceMetric that defines
                how to compute distances between points.
        kernel: An instance of Kernel that defines how the influence
                decays with distance.
    """

    def __init__(self, distance_metric: distance.DistanceMetric, kernel: kernels.Kernel, center: np.ndarray, weight: float = 1.0, name = None):

        if name is None:
          name = SourceField._generate_fallback_name()
        self.name = name
        self.distance_metric = distance_metric
        self.kernel = kernel
        self.center = np.asarray(center, dtype=float)
        self.weight = weight

    @staticmethod
    def _generate_fallback_name() -> str:
        global _unnamed_counter
        name = f"unnamed_factor_{_unnamed_counter}"
        _unnamed_counter += 1
        return name

    def __call__(self, points: np.ndarray) -> np.ndarray:
        """
        Evaluate the source field at given points.

        Args:
            points: A numpy array of shape (..., D) representing the points
                    at which to evaluate the field.

        Returns:
            A numpy array of shape (...) containing the evaluated field values.
        """
        return self.evaluate(points)

    def evaluate(self, points: np.ndarray) -> np.ndarray:
        """
        Evaluate the source field at given points relative to a center point.

        Args:
            points: A numpy array of shape (..., D) representing the points
                    at which to evaluate the field.
            center: A numpy array of shape (D,) representing the center point.

        Returns:
            A numpy array of shape (...) containing the evaluated field values.
        """
        print(self.name)
        distances = self.distance_metric(points, self.center)
        falloff =  self.kernel(distances)
        return self.weight * falloff
