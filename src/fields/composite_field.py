from . import distance
from . import kernels
from . import source_field
import numpy as np

class CompositeField():
    """
    A CompositeField is a combination of multiple SourceFields.
    It defines how to compute the combined influence of multiple source points on
    surrounding points in space.

    Attributes:
        source_fields: A list of SourceField instances that define the individual
                influences of each source point.
    """

    def __init__(self, source_fields: list):
        self.source_fields = source_fields

    def __call__(self, points: np.ndarray) -> np.ndarray:
        """
        Evaluate the composite field at given points.

        Args:
            points: A numpy array of shape (..., D) representing the points
                    at which to evaluate the field.

        Returns:
            A numpy array of shape (...) containing the evaluated field values.
        """
        return self.evaluate(points)

    def evaluate(self, points: np.ndarray) -> np.ndarray:
        """
        Evaluate the composite field at given points by summing the contributions
        from all source fields.

        Args:
            points: A numpy array of shape (..., D) representing the points
                    at which to evaluate the field.

        Returns:
            A numpy array of shape (...) containing the evaluated field values.
        """
        total_field = np.zeros(points.shape[:-1])
        for source in self.source_fields:
          total_field += source(points)
        return total_field
