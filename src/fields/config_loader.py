"""
config_loader.py

Reads a TOML config file, validates it via config_validation, and
constructs SourceField/CompositeField instances from a buildable
report. This is the final piece connecting raw config text to real,
queryable Field objects.
"""

import tomllib  # standard library in Python 3.11+, reads (not writes) TOML
import numpy as np

from .config_validation import validate_document, FATAL
from . import kernels
from . import distance
from .source_field import SourceField
from .composite_field import CompositeField

KNOWN_KERNEL_TYPES = set(kernels.KERNEL_REGISTRY.keys())
KNOWN_DISTANCE_TYPES = set(distance.DISTANCE_REGISTRY.keys())

KERNEL_BUILDERS = {
    "gaussian": lambda block: GaussianKernel(sigma=block["sigma"]),
    "inverse_square": lambda block: InverseSquareKernel(scale=block["scale"]),
    "compact_support": lambda block: CompactSupportKernel(radius=block["radius"]),
    "constant": lambda block: ConstantKernel(radius=block.get("radius")),
}

DISTANCE_BUILDERS = {
    "euclidean": lambda block: EuclideanDistance(),
    "anisotropic": lambda block: AnisotropicDistance.from_ellipse(
        a=block["a"], b=block["b"], angle_rad=block.get("angle_rad", 0.0)
    ),
}


class ConfigValidationError(Exception):
    """Raised when a config is not buildable. Carries the full report
    so a human can see every problem at once, not just the first."""

    def __init__(self, report):
        self.report = report
        fatal_count = sum(1 for i in report.issues if i.severity == FATAL)
        unapplied_count = sum(
            1 for i in report.issues if i.severity != FATAL and not i.applied
        )
        summary = "\n".join(
            f"  [{i.severity}] {i.identifier} -- {i.field}: {i.message}"
            for i in report.issues
        )
        super().__init__(
            f"Config not buildable: {fatal_count} fatal issue(s), "
            f"{unapplied_count} unapplied correction(s)\n{summary}"
        )


def _build_source_field(corrected_factor: dict) -> SourceField:
    kernel_block = corrected_factor["kernel"]
    distance_block = corrected_factor["distance"]

    kernel = KERNEL_BUILDERS[kernel_block["type"]](kernel_block)
    distance_metric = DISTANCE_BUILDERS[distance_block["type"]](distance_block)

    return SourceField(
        distance_metric=distance_metric,
        kernel=kernel,
        center=np.asarray(corrected_factor["center"], dtype=float),
        weight=corrected_factor["weight"],
        name=corrected_factor["name"],
    )


def load_composite_field_from_path(path: str, auto_correct: bool = True) -> CompositeField:
    with open(path, "rb") as f:
        toml_dict = tomllib.load(f)

    report = validate_document(toml_dict, auto_correct=auto_correct)

    for issue in report.issues:
        print(f"[{issue.severity}] {issue.identifier} -- {issue.field}: {issue.message}")

    if not report.is_buildable:
        raise ConfigValidationError(report)

    sources = [_build_source_field(factor) for factor in report.corrected_factors]
    return CompositeField(sources)
