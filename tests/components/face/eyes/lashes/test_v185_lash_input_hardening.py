import math

import pytest

from visual_engine.components.face.eyes.lashes.spec import LashSpec, LowerLashSpec


@pytest.mark.parametrize("field", [
    "density", "length", "thickness", "curvature", "spacing_jitter",
    "outer_flare", "inner_length_factor", "upward_bias", "taper",
])
def test_lash_real_fields_reject_nonfinite(field):
    for value in (math.nan, math.inf, -math.inf):
        with pytest.raises(ValueError):
            LashSpec(**{field: value})


@pytest.mark.parametrize("field", [
    "density", "length", "thickness", "curvature", "spacing_jitter",
    "outer_flare", "inner_length_factor", "upward_bias", "taper",
])
def test_lash_real_fields_reject_bool(field):
    with pytest.raises(ValueError):
        LashSpec(**{field: True})


@pytest.mark.parametrize("value", [True, False, 2.5, "18"])
def test_lash_count_rejects_non_integral_values(value):
    with pytest.raises(ValueError):
        LashSpec(count=value)


@pytest.mark.parametrize("field", [
    "density", "length", "thickness", "curvature", "opacity",
    "outer_flare", "downward_bias", "taper",
])
def test_lower_lash_real_fields_reject_nonfinite(field):
    for value in (math.nan, math.inf, -math.inf):
        with pytest.raises(ValueError):
            LowerLashSpec(**{field: value})


@pytest.mark.parametrize("value", [True, False, 2.5, "7"])
def test_lower_lash_count_rejects_non_integral_values(value):
    with pytest.raises(ValueError):
        LowerLashSpec(count=value)


def test_lash_valid_authored_values_remain_accepted():
    spec = LashSpec(count=0, length=0, thickness=0, spacing_jitter=0)
    assert spec.count == 0
    assert spec.length == 0


def test_lower_lash_valid_authored_values_remain_accepted():
    spec = LowerLashSpec(count=0, length=0, thickness=0, opacity=0)
    assert spec.count == 0
    assert spec.opacity == 0


def test_existing_style_and_form_validation_remains_active():
    with pytest.raises(ValueError):
        LashSpec(style="unknown")
    with pytest.raises(ValueError):
        LowerLashSpec(form="unknown")


def test_lash_enabled_rejects_coercive_types():
    for value in ("false", 1, 0, None):
        with pytest.raises(TypeError):
            LashSpec(enabled=value)


def test_lower_lash_enabled_rejects_coercive_types():
    for value in ("false", 1, 0, None):
        with pytest.raises(TypeError):
            LowerLashSpec(enabled=value)


@pytest.mark.parametrize("field", [
    "density", "length", "thickness", "curvature", "spacing_jitter",
    "outer_flare", "inner_length_factor", "upward_bias", "taper",
])
def test_lash_real_fields_reject_numeric_strings(field):
    with pytest.raises(ValueError):
        LashSpec(**{field: "0.5"})


@pytest.mark.parametrize("field", [
    "density", "length", "thickness", "curvature", "opacity",
    "outer_flare", "downward_bias", "taper",
])
def test_lower_lash_real_fields_reject_numeric_strings(field):
    with pytest.raises(ValueError):
        LowerLashSpec(**{field: "0.5"})
