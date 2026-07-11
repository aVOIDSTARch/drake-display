# tests/test_config_validation.py

from fields.config_validation import validate_factor

# A raw factor dict, anisotropic distance, deliberately missing angle_rad
raw = {
    "name": "test_ellipse",
    "weight": 1.0,
    "center": [0.0, 0.0],
    "kernel": {"type": "gaussian", "sigma": 1.0},
    "distance": {"type": "anisotropic", "a": 2.0, "b": 1.0},
    # note: no angle_rad key at all
}

issues, corrected = validate_factor(raw, pos_num=0, auto_correct=True)

# --- Check 1: the issue was actually detected and reported ---
angle_issues = [i for i in issues if i.field == "distance.angle_rad"]
print("Detected angle_rad issue:", len(angle_issues) == 1)
if angle_issues:
    print("  severity:", angle_issues[0].severity)
    print("  corrected_value:", angle_issues[0].corrected_value)
    print("  applied:", angle_issues[0].applied)

# --- Check 2: corrected dict actually has the fix ---
print("corrected has angle_rad:", "angle_rad" in corrected["distance"])
print("corrected angle_rad value:", corrected["distance"].get("angle_rad"))

# --- Check 3: THE CRITICAL ONE -- raw must be completely untouched ---
print("raw still missing angle_rad:", "angle_rad" not in raw["distance"])

# --- Check 4: prove they're now genuinely different dict objects, not aliases ---
print("raw['distance'] and corrected['distance'] are different objects:",
      raw["distance"] is not corrected["distance"])
