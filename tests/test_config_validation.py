from fields.config_validation import CORRECTABLE, FATAL, validate_document, validate_factor


def anisotropic_factor(**distance_extra):
    return {
        "name": "test_ellipse",
        "weight": 1.0,
        "center": [0.0, 0.0],
        "kernel": {"type": "gaussian", "sigma": 1.0},
        "distance": {"type": "anisotropic", "a": 2.0, "b": 1.0, **distance_extra},
    }


def euclidean_factor():
    return {
        "name": "test_circle",
        "weight": 1.0,
        "center": [0.0, 0.0],
        "kernel": {"type": "gaussian", "sigma": 1.0},
        "distance": {"type": "euclidean"},
    }


def test_missing_angle_rad_is_reported_and_corrected():
    raw = anisotropic_factor()
    issues, corrected = validate_factor(raw, pos_num=0, auto_correct=True)

    angle_issues = [i for i in issues if i.field == "distance.angle_rad"]
    assert len(angle_issues) == 1
    assert angle_issues[0].severity == CORRECTABLE
    assert angle_issues[0].corrected_value == 0.0
    assert angle_issues[0].applied
    assert corrected["distance"]["angle_rad"] == 0.0


def test_raw_input_is_never_mutated():
    raw = anisotropic_factor()
    _, corrected = validate_factor(raw, pos_num=0, auto_correct=True)
    assert "angle_rad" not in raw["distance"]
    assert raw["distance"] is not corrected["distance"]


def test_explicit_angle_rad_is_preserved():
    issues, corrected = validate_factor(anisotropic_factor(angle_rad=0.7), pos_num=0)
    assert issues == []
    assert corrected["distance"]["angle_rad"] == 0.7


def test_euclidean_distance_gets_no_angle_rad():
    issues, corrected = validate_factor(euclidean_factor(), pos_num=0)
    assert issues == []
    assert "angle_rad" not in corrected["distance"]


def test_unknown_kernel_type_is_fatal_with_suggestion():
    raw = euclidean_factor()
    raw["kernel"] = {"type": "gausian", "sigma": 1.0}
    issues, _ = validate_factor(raw, pos_num=0)
    [issue] = [i for i in issues if i.field == "kernel.type"]
    assert issue.severity == FATAL
    assert "did you mean 'gaussian'" in issue.message


def test_missing_center_is_fatal():
    raw = euclidean_factor()
    del raw["center"]
    report = validate_document({"factor": [raw]})
    assert not report.is_buildable
    assert any(i.field == "center" and i.severity == FATAL for i in report.issues)


def test_unapplied_correction_blocks_build():
    doc = {"factor": [anisotropic_factor()]}
    assert validate_document(doc, auto_correct=True).is_buildable
    assert not validate_document(doc, auto_correct=False).is_buildable
