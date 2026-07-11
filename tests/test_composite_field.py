# tests/test_composite_field.py

import numpy as np
from fields.kernels import GaussianKernel
from fields.distance import EuclideanDistance
from fields.source_field import SourceField
from fields.composite_field import CompositeField

# Two sources, both Gaussian sigma=1, weight=1, but at different centers
source_a = SourceField(
    distance_metric=EuclideanDistance(),
    kernel=GaussianKernel(sigma=1.0),
    center=np.array([0.0, 0.0]),
    weight=1.0
)

source_b = SourceField(
    distance_metric=EuclideanDistance(),
    kernel=GaussianKernel(sigma=1.0),
    center=np.array([2.0, 0.0]),
    weight=1.0
)

composite = CompositeField([source_a, source_b])

points = np.array([
    [0.0, 0.0],   # sits exactly on source_a
    [2.0, 0.0],   # sits exactly on source_b
    [1.0, 0.0],   # exactly halfway between the two
])

result = composite(points)
print(result)
