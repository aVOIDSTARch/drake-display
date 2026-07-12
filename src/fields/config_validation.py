"""
config_validation.py

Validates parsed TOML factor dictionaries against the SourceField/
CompositeField requirements, following the FATAL/CORRECTABLE severity
table established in design discussion. Produces a structured report
rather than a bare True/False, so every problem in a document surfaces
in one pass instead of failing on the first bad field.
"""

from dataclasses import dataclass, field
from difflib import get_close_matches
from typing import Any
from . import kernels
from . import distance
import itertools

FATAL = "FATAL"
CORRECTABLE = "CORRECTABLE"
MISSING = object()  # sentinel: distinct from None, which could be a legitimate stored value

KNOWN_KERNEL_TYPES = set(kernels.KERNEL_REGISTRY.keys())
KNOWN_DISTANCE_TYPES = set(distance.DISTANCE_REGISTRY.keys())

REQUIRED_PARAMS_BY_KERNEL_TYPE = {
    "gaussian": ["sigma"],
    "inverse_square": ["scale"],
    "compact_support": ["radius"],
    "constant": [],  # radius is optional there, per ConstantKernel's own design
}

REQUIRED_PARAMS_BY_DISTANCE_TYPE = {
    "euclidean": [],
    "anisotropic": ["a", "b"],  # angle_rad handled separately -- it's CORRECTABLE, not required
}

_unnamed_counter = itertools.count()


def generate_unnamed_fallback() -> str:
    return f"unnamed_factor_{next(_unnamed_counter)}"


def build_identifier(pos_num: int, name: str | None) -> str:
    return f"factor_at_pos_{pos_num}: {name if name is not None else None}"


@dataclass
class Issue:
    identifier: str
    severity: str          # FATAL or CORRECTABLE
    field: str              # e.g. "center", "kernel.sigma"
    found_value: Any
    corrected_value: Any
    applied: bool
    message: str


@dataclass
class ValidationReport:
    is_buildable: bool
    issues: list[Issue] = field(default_factory=list)
    corrected_factors: list[dict] = field(default_factory=list)


def validate_factor(raw: dict, pos_num: int, auto_correct: bool = True) -> tuple[list[Issue], dict]:
    issues: list[Issue] = []
    corrected = dict(raw)  # shallow copy -- never mutate the caller's original dict
    identifier = build_identifier(pos_num, raw.get("name"))

    # ---- name ----
    if raw.get("name") is None:
        fallback = generate_unnamed_fallback()
        issues.append(Issue(identifier, CORRECTABLE, "name", MISSING, fallback,
                             applied=auto_correct,
                             message="no name provided"))
        if auto_correct:
            corrected["name"] = fallback

    # ---- weight ----
    if "weight" not in raw:
        issues.append(Issue(identifier, CORRECTABLE, "weight", MISSING, 1.0,
                             applied=auto_correct,
                             message="no weight provided, defaulting to 1.0 -- verify this is intentional"))
        if auto_correct:
            corrected["weight"] = 1.0

    # ---- center ----
    if "center" not in raw:
        issues.append(Issue(identifier, FATAL, "center", MISSING, None, applied=False,
                             message="center is required -- no safe default location exists"))

    # ---- kernel ----
    kernel_block = raw.get("kernel", {})
    kernel_type = kernel_block.get("type")

    if kernel_type is None:
        issues.append(Issue(identifier, FATAL, "kernel.type", MISSING, None, applied=False,
                             message=f"kernel type missing -- must be one of {sorted(KNOWN_KERNEL_TYPES)}"))
    elif kernel_type not in KNOWN_KERNEL_TYPES:
        suggestion = get_close_matches(kernel_type, KNOWN_KERNEL_TYPES, n=1)
        hint = f" -- did you mean '{suggestion[0]}'?" if suggestion else ""
        issues.append(Issue(identifier, FATAL, "kernel.type", kernel_type, None, applied=False,
                             message=f"unrecognized kernel type{hint}"))
    else:
        for param in REQUIRED_PARAMS_BY_KERNEL_TYPE[kernel_type]:
            if param not in kernel_block:
                issues.append(Issue(identifier, FATAL, f"kernel.{param}", MISSING, None, applied=False,
                                     message=f"'{kernel_type}' kernel requires '{param}', no safe default"))

    # ---- distance ----
    distance_block = raw.get("distance", {})
    distance_type = distance_block.get("type")

    if distance_type is None:
        issues.append(Issue(identifier, FATAL, "distance.type", MISSING, None, applied=False,
                             message=f"distance type missing -- must be one of {sorted(KNOWN_DISTANCE_TYPES)}"))
    elif distance_type not in KNOWN_DISTANCE_TYPES:
        suggestion = get_close_matches(distance_type, KNOWN_DISTANCE_TYPES, n=1)
        hint = f" -- did you mean '{suggestion[0]}'?" if suggestion else ""
        issues.append(Issue(identifier, FATAL, "distance.type", distance_type, None, applied=False,
                             message=f"unrecognized distance type{hint}"))
    else:
        for param in REQUIRED_PARAMS_BY_DISTANCE_TYPE[distance_type]:
            if param not in distance_block:
                issues.append(Issue(identifier, FATAL, f"distance.{param}", MISSING, None, applied=False,
                                     message=f"'{distance_type}' distance requires '{param}', no safe default"))

    if distance_type == "anisotropic" and "angle_rad" not in distance_block:
      issues.append(Issue(identifier,
                          CORRECTABLE,
                          "distance.angle_rad",
                          MISSING, 0.0,
                          applied=auto_correct,
                          message="no rotation given, defaulting to 0.0 (unrotated)"))
    if auto_correct:
        new_distance = dict(distance_block)   # explicit fresh copy, always
        new_distance["angle_rad"] = 0.0
        corrected["distance"] = new_distance  # explicit reassignment, not setdefault

    return issues, corrected


def validate_document(toml_dict: dict, auto_correct: bool = True) -> ValidationReport:
    all_issues: list[Issue] = []
    corrected_factors: list[dict] = []

    for pos_num, raw_factor in enumerate(toml_dict.get("factor", [])):
        issues, corrected = validate_factor(raw_factor, pos_num, auto_correct)
        all_issues.extend(issues)
        corrected_factors.append(corrected)

    has_fatal = any(i.severity == FATAL for i in all_issues)
    has_unapplied_correctable = any(i.severity == CORRECTABLE and not i.applied for i in all_issues)
    is_buildable = not has_fatal and not has_unapplied_correctable

    return ValidationReport(is_buildable, all_issues, corrected_factors)
