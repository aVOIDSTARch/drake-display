import numpy as np
import pytest
from fields.composite_field import CompositeField
from fields.config_loader import ConfigValidationError, load_composite_field_from_path

GOOD_TOML = """
[[factor]]
name = "core"
weight = 2.0
center = [0.0, 0.0]
kernel = { type = "gaussian", sigma = 1.0 }
distance = { type = "euclidean" }

[[factor]]
name = "ellipse"
weight = 1.0
center = [3.0, 0.0]
kernel = { type = "compact_support", radius = 1.0 }
distance = { type = "anisotropic", a = 2.0, b = 1.0, angle_rad = 0.5 }
"""

BAD_TOML = """
[[factor]]
name = "broken"
kernel = { type = "gaussian" }
distance = { type = "euclidean" }
"""


def test_loads_valid_config_into_composite(tmp_path):
    path = tmp_path / "good.toml"
    path.write_text(GOOD_TOML)

    field = load_composite_field_from_path(str(path))

    assert isinstance(field, CompositeField)
    assert [s.name for s in field.source_fields] == ["core", "ellipse"]
    np.testing.assert_allclose(field(np.array([[0.0, 0.0]])), [2.0])


def test_invalid_config_raises_with_full_report(tmp_path):
    path = tmp_path / "bad.toml"
    path.write_text(BAD_TOML)

    with pytest.raises(ConfigValidationError) as excinfo:
        load_composite_field_from_path(str(path))

    fields_reported = {i.field for i in excinfo.value.report.issues}
    assert {"center", "kernel.sigma", "weight"} <= fields_reported
