"""
registry.py

Entities + configs -> the factor registry (plan-phase0 8:
factors.build_registry). Galactic-smooth factors come from
configs/phase0-galactic.toml; one FAC-SN factor is generated per
massive-progenitor entity, carrying that entity's own position, clock
and field confidences.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from fields.config_loader import load_log_odds_field_from_path
from fields.distance import EuclideanDistance
from fields.factor import Factor
from fields.kernels import TruncatedInverseSquareKernel
from fields.log_odds_field import LogOddsField
from fields.source_field import SourceField
from fields.temporal import RampSpikeDecayProfile

# FAC-SN, factors.md section 2 and Appendix A
SN_SIGN = -1
SN_MAGNITUDE = 1.0
SN_BACKING = 0.9
SN_KILL_RADIUS_KPC = 0.010
SN_DECAY_MYR = 2.0


def supernova_factor(entity: pd.Series) -> Factor:
    """One FAC-SN term for a massive-progenitor entity row."""
    center = entity[["x_gal_kpc", "y_gal_kpc", "z_gal_kpc"]].to_numpy(dtype=float)
    return Factor(
        name=f"FAC-SN {entity['name']}",
        spatial=SourceField(EuclideanDistance(), TruncatedInverseSquareKernel(SN_KILL_RADIUS_KPC),
                            center=center, name=entity["name"]),
        sign=SN_SIGN,
        backing=SN_BACKING,
        magnitude=SN_MAGNITUDE,
        temporal=RampSpikeDecayProfile(entity["t_birth_myr"], entity["t_collapse_myr"], SN_DECAY_MYR),
        input_confidences={
            "position": entity["conf_position"],
            "mass_msun": entity["conf_mass_msun"],
            "t_collapse_myr": entity["conf_clock"],
        },
    )


def build_hazard_field(entities: pd.DataFrame) -> LogOddsField:
    progenitors = entities[entities["kind"] == "star_massive_progenitor"]
    return LogOddsField([supernova_factor(row) for _, row in progenitors.iterrows()], baseline=0.0)


def build_fields(entities: pd.DataFrame, config_dir: Path) -> tuple[LogOddsField, LogOddsField]:
    """(galactic, local): the smooth whole-disk field, and that same field
    plus every point hazard, for the local-zoom regime (ADR-004)."""
    galactic = load_log_odds_field_from_path(str(config_dir / "phase0-galactic.toml"))
    local = LogOddsField.combine([galactic, build_hazard_field(entities)])
    return galactic, local


def evaluate_at_entities(field: LogOddsField, entities: pd.DataFrame, t: float) -> pd.DataFrame:
    """entity.md group 10: habitability_here, confidence_here, logit_here
    at each entity's own position."""
    points = entities[["x_gal_kpc", "y_gal_kpc", "z_gal_kpc"]].to_numpy(dtype=float)
    sample = field(points, t)
    return pd.DataFrame({
        "habitability_here": sample.height,
        "confidence_here": sample.confidence,
        "logit_here": sample.logit,
    }, index=entities.index)


def near(entities: pd.DataFrame, center, half_width_kpc: float) -> pd.DataFrame:
    """Entities whose (x, y) falls inside a square patch around center."""
    cx, cy = center[0], center[1]
    inside = ((np.abs(entities["x_gal_kpc"] - cx) <= half_width_kpc)
              & (np.abs(entities["y_gal_kpc"] - cy) <= half_width_kpc))
    return entities[inside]
