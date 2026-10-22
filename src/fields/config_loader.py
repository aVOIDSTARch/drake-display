"""
config_loader.py

Reads a TOML config file, validates it via config_validation, and
constructs SourceField/CompositeField instances (or Factor/
LogOddsField instances, for log-odds documents) from a buildable
report. This is the final piece connecting raw config text to real,
queryable Field objects.
"""

import tomllib  # standard library in Python 3.11+, reads (not writes) TOML
import numpy as np

from .config_validation import validate_document, validate_log_odds_document, FATAL
from . import kernels
from . import distance
from . import temporal
from .source_field import SourceField
from .composite_field import CompositeField
from .factor import Factor
from .log_odds_field import LogOddsField

KERNEL_BUILDERS = {
    "gaussian": lambda block: kernels.GaussianKernel(sigma=block["sigma"]),
    "inverse_square": lambda block: kernels.InverseSquareKernel(scale=block["scale"]),
    "compact_support": lambda block: kernels.CompactSupportKernel(radius=block["radius"]),
    "constant": lambda block: kernels.ConstantKernel(radius=block.get("radius")),
    "exponential": lambda block: kernels.ExponentialKernel(scale=block["scale"]),
    "logistic_step": lambda block: kernels.LogisticStepKernel(
        radius=block["radius"], width=block["width"]
    ),
    "truncated_inverse_square": lambda block: kernels.TruncatedInverseSquareKernel(
        kill_radius=block["kill_radius"], cutoff_factor=block.get("cutoff_factor", 5.0)
    ),
    "metallicity_band": lambda block: kernels.MetallicityBandKernel(
        **{k: v for k, v in block.items() if k != "type"}
    ),
}

DISTANCE_BUILDERS = {
    "euclidean": lambda block: distance.EuclideanDistance(),
    "anisotropic": lambda block: distance.AnisotropicDistance.from_ellipse(
        a=block["a"], b=block["b"], angle_rad=block.get("angle_rad", 0.0)
    ),
    "cylindrical": lambda block: distance.CylindricalDistance(),
    "disk_scaled": lambda block: distance.DiskScaledDistance(h_R=block["h_R"], h_z=block["h_z"]),
}


def _build_ramp_spike_decay(block: dict) -> temporal.RampSpikeDecayProfile:
    if "mass_msun" in block:
        return temporal.RampSpikeDecayProfile.from_mass(
            t_birth_myr=block["t_birth_myr"], mass_msun=block["mass_msun"],
            decay_myr=block["decay_myr"],
        )
    return temporal.RampSpikeDecayProfile(
        t_birth_myr=block["t_birth_myr"], t_collapse_myr=block["t_collapse_myr"],
        decay_myr=block["decay_myr"],
    )


TEMPORAL_BUILDERS = {
    "static": lambda block: temporal.StaticProfile(),
    "ramp_spike_decay": _build_ramp_spike_decay,
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


def _print_issues(report) -> None:
    for issue in report.issues:
        print(f"[{issue.severity}] {issue.identifier} -- {issue.field}: {issue.message}")


def _build_source_field(corrected_factor: dict, weight: float) -> SourceField:
    kernel_block = corrected_factor["kernel"]
    distance_block = corrected_factor["distance"]

    kernel = KERNEL_BUILDERS[kernel_block["type"]](kernel_block)
    distance_metric = DISTANCE_BUILDERS[distance_block["type"]](distance_block)

    return SourceField(
        distance_metric=distance_metric,
        kernel=kernel,
        center=np.asarray(corrected_factor["center"], dtype=float),
        weight=weight,
        name=corrected_factor["name"],
    )


def _build_factor(corrected_factor: dict) -> Factor:
    temporal_block = corrected_factor["temporal"]
    return Factor(
        name=corrected_factor["name"],
        # weight 1.0: strength lives in sign/backing/magnitude, not the spatial profile
        spatial=_build_source_field(corrected_factor, weight=1.0),
        sign=int(corrected_factor["sign"]),
        backing=corrected_factor["backing"],
        magnitude=corrected_factor["magnitude"],
        temporal=TEMPORAL_BUILDERS[temporal_block["type"]](temporal_block),
        input_confidences=dict(corrected_factor["inputs"]),
    )


def load_composite_field_from_path(path: str, auto_correct: bool = True) -> CompositeField:
    with open(path, "rb") as f:
        toml_dict = tomllib.load(f)

    report = validate_document(toml_dict, auto_correct=auto_correct)
    _print_issues(report)

    if not report.is_buildable:
        raise ConfigValidationError(report)

    sources = [_build_source_field(factor, factor["weight"]) for factor in report.corrected_factors]
    return CompositeField(sources)


def load_log_odds_field_from_path(path: str, auto_correct: bool = True) -> LogOddsField:
    with open(path, "rb") as f:
        toml_dict = tomllib.load(f)

    report = validate_log_odds_document(toml_dict, auto_correct=auto_correct)
    _print_issues(report)

    if not report.is_buildable:
        raise ConfigValidationError(report)

    factors = [_build_factor(factor) for factor in report.corrected_factors]
    return LogOddsField(factors, baseline=report.baseline)
