import math

import pytest

from visual_engine.components.face.eyes.eyebrow.spec import BrowSpec


@pytest.mark.parametrize("field", [
    "length", "thickness", "density", "angle_deg", "x", "y", "ornament",
    "fade_at_inner", "fade_at_outer", "min_eye_gap", "max_eye_gap",
])
@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_real_fields_reject_nonfinite(field, value):
    with pytest.raises(ValueError):
        BrowSpec(**{field: value})


@pytest.mark.parametrize("field", [
    "length", "thickness", "density", "angle_deg", "x", "y", "ornament",
    "fade_at_inner", "fade_at_outer", "min_eye_gap", "max_eye_gap",
])
def test_real_fields_reject_bool(field):
    with pytest.raises(ValueError):
        BrowSpec(**{field: True})


@pytest.mark.parametrize("field", [
    "length", "thickness", "density", "angle_deg", "x", "y", "ornament",
    "fade_at_inner", "fade_at_outer", "min_eye_gap", "max_eye_gap",
])
def test_real_fields_reject_numeric_strings(field):
    with pytest.raises(ValueError):
        BrowSpec(**{field: "0.5"})


@pytest.mark.parametrize("field", [
    "length", "thickness", "density", "angle_deg", "x", "y", "ornament",
    "fade_at_inner", "fade_at_outer", "min_eye_gap", "max_eye_gap",
])
def test_real_fields_reject_float_overflow_integers(field):
    with pytest.raises(ValueError):
        BrowSpec(**{field: 10**10000})


@pytest.mark.parametrize("value", [1, 0, "true", None])
def test_enabled_requires_real_bool(value):
    with pytest.raises(TypeError):
        BrowSpec(enabled=value)


def test_existing_valid_values_remain_valid():
    brow = BrowSpec(
        enabled=True,
        shape="high_arch",
        length=0.85,
        thickness=0.08,
        density=0.85,
        angle_deg=7.5,
        x=0.03,
        y=-0.4,
        ornament=0.2,
        fade_at_inner=0.1,
        fade_at_outer=0.2,
        min_eye_gap=0.18,
        max_eye_gap=0.60,
    )
    assert brow.shape == "high_arch"
    assert brow.length == pytest.approx(0.85)
    assert brow.max_eye_gap == pytest.approx(0.60)


def test_immutable_value_contract_is_preserved():
    brow = BrowSpec()
    with pytest.raises((AttributeError, TypeError)):
        brow.length = 0.5
