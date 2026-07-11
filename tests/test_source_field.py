# smoke test for SourceField — combining a real Kernel + DistanceMetric

import numpy as np
from fields.kernels import GaussianKernel
from fields.distance import EuclideanDistance
from fields.source_field import SourceField

# A single source: Gaussian falloff, sigma=1, centered at (0,0), weight=2.0
source = SourceField(
    distance_metric=EuclideanDistance(),
    kernel=GaussianKernel(sigma=1.0),
    center=np.array([0.0, 0.0]),
    weight=2.0
)

points = np.array([
    [0.0, 0.0],   # exactly at the source
    [1.0, 0.0],   # distance 1
    [0.0, 2.0],   # distance 2
])

result = source(points)
print(result)

