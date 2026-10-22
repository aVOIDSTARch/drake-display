from pathlib import Path

import numpy as np
import pytest
from fields.config_loader import ConfigValidationError, load_log_odds_field_from_path
from fields.config_validation import (
    CORRECTABLE,
    FATAL,
    validate_log_odds_document,
    validate_log_odds_factor,
)
from fields.log_odds_field import LogOddsField
from fields.temporal import RampSpikeDecayProfile, StaticProfile

PHASE0_CONFIG = str(Path(__file__).parent.parent / "configs" / "phase0-galactic.toml")


def supernova_factor(**overrides):
    raw = {
        "name": "FAC-SN",
        "sign": -1,
        "magnitude": 1.0,
        "backing": 0.9,
        "center": [0.0, 0.0],
        "kernel": {"type": "compact_support", "radius": 0.05},
        "distance": {"type": "euclidean"},
        "temporal": {"type": "ramp_spike_decay", "t_birth_myr": 0.0, "mass_msun": 20.0,
                     "decay_myr": 2.0},
        "inputs": {"mass_msun": 0.5},
    }
    raw.update(overrides)
    return raw


def fields_with(issues, severity):
    return {i.field for i in issues if i.severity == severity}


def test_complete_factor_has_no_issues():
    issues, _ = validate_log_odds_factor(supernova_factor(), pos_num=0)
    assert issues == []


@pytest.mark.parametrize("missing", ["sign", "backing", "magnitude"])
def test_strength_terms_are_fatal_when_missing(missing):
    raw = supernova_factor()
    del raw[missing]
    issues, _ = validate_log_odds_factor(raw, pos_num=0)
    assert missing in fields_with(issues, FATAL)


@pytest.mark.parametrize("field,value", [("sign", 0), ("sign", True), ("backing", 1.5),
                                         ("magnitude", -1.0)])
def test_out_of_range_strength_terms_are_fatal(field, value):
    issues, _ = validate_log_odds_factor(supernova_factor(**{field: value}), pos_num=0)
    assert field in fields_with(issues, FATAL)


def test_weight_is_rejected_in_log_odds_factor():
    issues, _ = validate_log_odds_factor(supernova_factor(weight=1.0), pos_num=0)
    assert "weight" in fields_with(issues, FATAL)


def test_missing_temporal_and_inputs_are_correctable():
    raw = supernova_factor()
    del raw["temporal"], raw["inputs"]
    issues, corrected = validate_log_odds_factor(raw, pos_num=0)
    assert fields_with(issues, CORRECTABLE) == {"temporal", "inputs"}
    assert corrected["temporal"] == {"type": "static"}
    assert corrected["inputs"] == {}
    assert "temporal" not in raw


@pytest.mark.parametrize("clock", [
    {"type": "ramp_spike_decay", "t_birth_myr": 0.0},
    {"type": "ramp_spike_decay", "t_birth_myr": 0.0, "mass_msun": 20.0, "t_collapse_myr": 5.0},
])
def test_ramp_needs_exactly_one_collapse_source(clock):
    issues, _ = validate_log_odds_factor(supernova_factor(temporal=clock), pos_num=0)
    assert "temporal.t_collapse_myr" in fields_with(issues, FATAL)


def test_missing_decay_is_corrected_without_mutating_input():
    clock = {"type": "ramp_spike_decay", "t_birth_myr": 0.0, "mass_msun": 20.0}
    raw = supernova_factor(temporal=clock)
    issues, corrected = validate_log_odds_factor(raw, pos_num=0)
    assert fields_with(issues, CORRECTABLE) == {"temporal.decay_myr"}
    assert corrected["temporal"]["decay_myr"] == 2.0
    assert "decay_myr" not in clock


def test_missing_baseline_is_correctable():
    report = validate_log_odds_document({"factor": [supernova_factor()]})
    assert report.is_buildable
    assert report.baseline == 0.0
    assert fields_with(report.issues, CORRECTABLE) == {"baseline"}


def test_phase0_galactic_config_builds():
    field = load_log_odds_field_from_path(PHASE0_CONFIG)

    assert isinstance(field, LogOddsField)
    assert [f.name for f in field.factors] == ["FAC-METAL", "FAC-DENSITY", "FAC-AGN"]
    assert all(isinstance(f.temporal, StaticProfile) for f in field.factors)
    assert [f.sign for f in field.factors] == [1, -1, -1]

    sample = field(np.array([[8.2, 0.0, 0.02], [0.0, 0.0, 0.0]]), t=0.0)
    assert np.all((sample.height > 0) & (sample.height < 1))
    assert np.all((sample.confidence >= 0) & (sample.confidence <= 1))


def test_ramp_factor_builds_from_mass(tmp_path):
    path = tmp_path / "sn.toml"
    path.write_text("""
baseline = 0.0
[[factor]]
name = "FAC-SN"
sign = -1
magnitude = 1.0
backing = 0.9
center = [0.0, 0.0]
kernel = { type = "compact_support", radius = 0.05 }
distance = { type = "euclidean" }
temporal = { type = "ramp_spike_decay", t_birth_myr = 0.0, mass_msun = 20.0, decay_myr = 2.0 }
inputs = { mass_msun = 0.5 }
""")
    [factor] = load_log_odds_field_from_path(str(path)).factors
    assert isinstance(factor.temporal, RampSpikeDecayProfile)
    assert factor.temporal.t_collapse_myr == pytest.approx(5.59, abs=0.01)
    assert factor.spatial.weight == 1.0


def test_composite_style_document_is_not_a_valid_log_odds_document(tmp_path):
    path = tmp_path / "old.toml"
    path.write_text("""
[[factor]]
name = "core"
weight = 2.0
center = [0.0, 0.0]
kernel = { type = "gaussian", sigma = 1.0 }
distance = { type = "euclidean" }
""")
    with pytest.raises(ConfigValidationError):
        load_log_odds_field_from_path(str(path))
