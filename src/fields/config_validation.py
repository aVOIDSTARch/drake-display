"""
config_validation.py

Validates parsed TOML factor dictionaries against the SourceField/
CompositeField requirements, following the FATAL/CORRECTABLE severity
table established in design discussion. Produces a structured report
rather than a bare True/False, so every problem in a document surfaces
in one pass instead of failing on the first bad field.

Two document kinds share the same spatial checks (center, kernel,
distance):
  - composite documents: factors carry a single "weight"
    (validate_factor / validate_document)
  - log-odds documents: factors carry sign, backing, magnitude,
    temporal and inputs instead (validate_log_odds_factor /
    validate_log_odds_document)
"""

from dataclasses import dataclass, field
from difflib import get_close_matches
from typing import Any
from . import kernels
from . import distance
from . import temporal
from ._naming import generate_unnamed_fallback

FATAL = "FATAL"
CORRECTABLE = "CORRECTABLE"
MISSING = object()  # sentinel: distinct from None, which could be a legitimate stored value

KNOWN_KERNEL_TYPES = set(kernels.KERNEL_REGISTRY.keys())
KNOWN_DISTANCE_TYPES = set(distance.DISTANCE_REGISTRY.keys())
KNOWN_TEMPORAL_TYPES = set(temporal.TEMPORAL_REGISTRY.keys())

REQUIRED_PARAMS_BY_KERNEL_TYPE = {
    "gaussian": ["sigma"],
    "inverse_square": ["scale"],
    "compact_support": ["radius"],
    "constant": [],  # radius is optional there, per ConstantKernel's own design
    "exponential": ["scale"],
    "logistic_step": ["radius", "width"],
    "metallicity_band": [],  # every parameter has a factors.md Appendix A default
    "truncated_inverse_square": ["kill_radius"],  # cutoff_factor optional, defaults to 5
}

REQUIRED_PARAMS_BY_DISTANCE_TYPE = {
    "euclidean": [],
    "anisotropic": ["a", "b"],  # angle_rad handled separately -- it's CORRECTABLE, not required
    "cylindrical": [],
    "disk_scaled": ["h_R", "h_z"],
}

DEFAULT_DECAY_MYR = 2.0
DEFAULT_BASELINE = 0.0


def build_identifier(pos_num: int, name: str | None) -> str:
    return f"factor_at_pos_{pos_num}: {name if name is not None else None}"


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


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
    baseline: float | None = None  # log-odds documents only


def _check_typed_block(block: dict, block_name: str, known_types: set[str],
                       required_params: dict[str, list[str]], identifier: str,
                       issues: list[Issue]) -> str | None:
    """Shared check for a {type = ..., params...} block. Returns the
    block's type if it is recognized, else None."""
    block_type = block.get("type")

    if block_type is None:
        issues.append(Issue(identifier, FATAL, f"{block_name}.type", MISSING, None, applied=False,
                             message=f"{block_name} type missing -- must be one of {sorted(known_types)}"))
        return None
    if block_type not in known_types:
        suggestion = get_close_matches(block_type, known_types, n=1)
        hint = f" -- did you mean '{suggestion[0]}'?" if suggestion else ""
        issues.append(Issue(identifier, FATAL, f"{block_name}.type", block_type, None, applied=False,
                             message=f"unrecognized {block_name} type{hint}"))
        return None
    for param in required_params.get(block_type, []):
        if param not in block:
            issues.append(Issue(identifier, FATAL, f"{block_name}.{param}", MISSING, None, applied=False,
                                 message=f"'{block_type}' {block_name} requires '{param}', no safe default"))
    return block_type


def _validate_name(raw: dict, identifier: str, auto_correct: bool,
                   issues: list[Issue], corrected: dict) -> None:
    if raw.get("name") is None:
        fallback = generate_unnamed_fallback()
        issues.append(Issue(identifier, CORRECTABLE, "name", MISSING, fallback,
                             applied=auto_correct,
                             message="no name provided"))
        if auto_correct:
            corrected["name"] = fallback


def _validate_spatial(raw: dict, identifier: str, auto_correct: bool,
                      issues: list[Issue], corrected: dict) -> None:
    # ---- center ----
    if "center" not in raw:
        issues.append(Issue(identifier, FATAL, "center", MISSING, None, applied=False,
                             message="center is required -- no safe default location exists"))

    # ---- kernel ----
    _check_typed_block(raw.get("kernel", {}), "kernel", KNOWN_KERNEL_TYPES,
                       REQUIRED_PARAMS_BY_KERNEL_TYPE, identifier, issues)

    # ---- distance ----
    distance_block = raw.get("distance", {})
    distance_type = _check_typed_block(distance_block, "distance", KNOWN_DISTANCE_TYPES,
                                       REQUIRED_PARAMS_BY_DISTANCE_TYPE, identifier, issues)

    if distance_type == "anisotropic" and "angle_rad" not in distance_block:
        issues.append(Issue(identifier, CORRECTABLE, "distance.angle_rad", MISSING, 0.0,
                             applied=auto_correct,
                             message="no rotation given, defaulting to 0.0 (unrotated)"))
        if auto_correct:
            new_distance = dict(distance_block)   # explicit fresh copy, always
            new_distance["angle_rad"] = 0.0
            corrected["distance"] = new_distance  # explicit reassignment, not setdefault


def validate_factor(raw: dict, pos_num: int, auto_correct: bool = True) -> tuple[list[Issue], dict]:
    issues: list[Issue] = []
    corrected = dict(raw)  # shallow copy -- never mutate the caller's original dict
    identifier = build_identifier(pos_num, raw.get("name"))

    _validate_name(raw, identifier, auto_correct, issues, corrected)

    # ---- weight ----
    if "weight" not in raw:
        issues.append(Issue(identifier, CORRECTABLE, "weight", MISSING, 1.0,
                             applied=auto_correct,
                             message="no weight provided, defaulting to 1.0 -- verify this is intentional"))
        if auto_correct:
            corrected["weight"] = 1.0

    _validate_spatial(raw, identifier, auto_correct, issues, corrected)

    return issues, corrected


def _validate_temporal(raw: dict, identifier: str, auto_correct: bool,
                       issues: list[Issue], corrected: dict) -> None:
    if "temporal" not in raw:
        issues.append(Issue(identifier, CORRECTABLE, "temporal", MISSING, {"type": "static"},
                             applied=auto_correct,
                             message="no temporal profile given, defaulting to static -- "
                                     "verify this factor really doesn't evolve"))
        if auto_correct:
            corrected["temporal"] = {"type": "static"}
        return

    temporal_block = raw["temporal"]
    temporal_type = _check_typed_block(temporal_block, "temporal", KNOWN_TEMPORAL_TYPES,
                                       {"ramp_spike_decay": ["t_birth_myr"]}, identifier, issues)
    if temporal_type != "ramp_spike_decay":
        return

    has_collapse = "t_collapse_myr" in temporal_block
    has_mass = "mass_msun" in temporal_block
    if has_collapse == has_mass:
        issues.append(Issue(identifier, FATAL, "temporal.t_collapse_myr", MISSING, None, applied=False,
                             message="ramp_spike_decay needs exactly one of 't_collapse_myr' or "
                                     "'mass_msun' (collapse time derived via EQ-STAR-1)"))

    if "decay_myr" not in temporal_block:
        issues.append(Issue(identifier, CORRECTABLE, "temporal.decay_myr", MISSING, DEFAULT_DECAY_MYR,
                             applied=auto_correct,
                             message=f"no remnant decay time given, defaulting to {DEFAULT_DECAY_MYR} Myr"))
        if auto_correct:
            new_temporal = dict(temporal_block)
            new_temporal["decay_myr"] = DEFAULT_DECAY_MYR
            corrected["temporal"] = new_temporal


def validate_log_odds_factor(raw: dict, pos_num: int,
                             auto_correct: bool = True) -> tuple[list[Issue], dict]:
    issues: list[Issue] = []
    corrected = dict(raw)  # shallow copy -- never mutate the caller's original dict
    identifier = build_identifier(pos_num, raw.get("name"))

    _validate_name(raw, identifier, auto_correct, issues, corrected)

    # ---- weight: ambiguous in a log-odds factor ----
    if "weight" in raw:
        issues.append(Issue(identifier, FATAL, "weight", raw["weight"], None, applied=False,
                             message="log-odds factors use sign, backing and magnitude instead of "
                                     "weight -- split it explicitly"))

    # ---- sign ----
    sign = raw.get("sign", MISSING)
    if sign is MISSING:
        issues.append(Issue(identifier, FATAL, "sign", MISSING, None, applied=False,
                             message="sign is required (+1 raises, -1 lowers) -- no safe default direction"))
    elif not _is_number(sign) or sign not in (1, -1):
        issues.append(Issue(identifier, FATAL, "sign", sign, None, applied=False,
                             message="sign must be +1 or -1"))

    # ---- backing ----
    backing = raw.get("backing", MISSING)
    if backing is MISSING:
        issues.append(Issue(identifier, FATAL, "backing", MISSING, None, applied=False,
                             message="backing is required -- there is no honest default science confidence"))
    elif not _is_number(backing) or not 0.0 <= backing <= 1.0:
        issues.append(Issue(identifier, FATAL, "backing", backing, None, applied=False,
                             message="backing must be a number in [0, 1]"))

    # ---- magnitude ----
    magnitude = raw.get("magnitude", MISSING)
    if magnitude is MISSING:
        issues.append(Issue(identifier, FATAL, "magnitude", MISSING, None, applied=False,
                             message="magnitude is required -- no safe default strength"))
    elif not _is_number(magnitude) or magnitude < 0:
        issues.append(Issue(identifier, FATAL, "magnitude", magnitude, None, applied=False,
                             message="magnitude must be a non-negative number"))

    # ---- inputs: entity-field confidences for EQ-CORE-4 ----
    if "inputs" not in raw:
        issues.append(Issue(identifier, CORRECTABLE, "inputs", MISSING, {},
                             applied=auto_correct,
                             message="no input confidences declared -- the default low "
                                     "per-field confidence will be assumed"))
        if auto_correct:
            corrected["inputs"] = {}
    else:
        for field_name, c in raw["inputs"].items():
            if not _is_number(c) or not 0.0 <= c <= 1.0:
                issues.append(Issue(identifier, FATAL, f"inputs.{field_name}", c, None, applied=False,
                                     message="input confidence must be a number in [0, 1]"))

    _validate_temporal(raw, identifier, auto_correct, issues, corrected)
    _validate_spatial(raw, identifier, auto_correct, issues, corrected)

    return issues, corrected


def _finish_report(all_issues: list[Issue], corrected_factors: list[dict],
                   baseline: float | None = None) -> ValidationReport:
    has_fatal = any(i.severity == FATAL for i in all_issues)
    has_unapplied_correctable = any(i.severity == CORRECTABLE and not i.applied for i in all_issues)
    is_buildable = not has_fatal and not has_unapplied_correctable

    return ValidationReport(is_buildable, all_issues, corrected_factors, baseline)


def validate_document(toml_dict: dict, auto_correct: bool = True) -> ValidationReport:
    all_issues: list[Issue] = []
    corrected_factors: list[dict] = []

    for pos_num, raw_factor in enumerate(toml_dict.get("factor", [])):
        issues, corrected = validate_factor(raw_factor, pos_num, auto_correct)
        all_issues.extend(issues)
        corrected_factors.append(corrected)

    return _finish_report(all_issues, corrected_factors)


def validate_log_odds_document(toml_dict: dict, auto_correct: bool = True) -> ValidationReport:
    all_issues: list[Issue] = []
    corrected_factors: list[dict] = []

    baseline = toml_dict.get("baseline", MISSING)
    if baseline is MISSING:
        all_issues.append(Issue("document", CORRECTABLE, "baseline", MISSING, DEFAULT_BASELINE,
                                applied=auto_correct,
                                message=f"no baseline log-odds given, defaulting to {DEFAULT_BASELINE}"))
        baseline = DEFAULT_BASELINE if auto_correct else None
    elif not _is_number(baseline):
        all_issues.append(Issue("document", FATAL, "baseline", baseline, None, applied=False,
                                message="baseline must be a number"))
        baseline = None

    for pos_num, raw_factor in enumerate(toml_dict.get("factor", [])):
        issues, corrected = validate_log_odds_factor(raw_factor, pos_num, auto_correct)
        all_issues.extend(issues)
        corrected_factors.append(corrected)

    return _finish_report(all_issues, corrected_factors, baseline)
