import math

import pytest

from visual_engine.components.face.eyes.eyelid.spec import EyelidAppearance


REAL_FIELDS = (
    "upper_width", "lower_width", "upper_opacity", "lower_opacity",
    "upper_crease_offset", "lower_crease_offset",
    "upper_crease_length", "lower_crease_length",
    "upper_crease_width", "lower_crease_width",
    "upper_crease_opacity", "lower_crease_opacity",
)
BOOL_FIELDS = (
    "upper_enabled", "lower_enabled", "upper_crease_enabled", "lower_crease_enabled",
)


@pytest.mark.parametrize("field", REAL_FIELDS)
@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_eyelid_real_fields_reject_nonfinite(field, value):
    with pytest.raises(ValueError):
        EyelidAppearance(**{field: value})


@pytest.mark.parametrize("field", REAL_FIELDS)
def test_eyelid_real_fields_reject_bool(field):
    with pytest.raises(ValueError):
        EyelidAppearance(**{field: True})


@pytest.mark.parametrize("field", REAL_FIELDS)
def test_eyelid_real_fields_reject_coercive_string(field):
    with pytest.raises(ValueError):
        EyelidAppearance(**{field: "0.5"})


@pytest.mark.parametrize("field", BOOL_FIELDS)
@pytest.mark.parametrize("value", [0, 1, "true", None])
def test_eyelid_boolean_fields_reject_non_bool(field, value):
    with pytest.raises(TypeError):
        EyelidAppearance(**{field: value})


def test_eyelid_valid_boundaries_are_preserved():
    spec = EyelidAppearance(
        upper_enabled=False,
        lower_enabled=False,
        upper_width=0,
        lower_width=0,
        upper_opacity=0,
        lower_opacity=1,
        upper_crease_enabled=False,
        lower_crease_enabled=True,
        upper_crease_offset=0,
        lower_crease_offset=0,
        upper_crease_length=1,
        lower_crease_length=1,
        upper_crease_width=0,
        lower_crease_width=0,
        upper_crease_opacity=0,
        lower_crease_opacity=1,
    )
    assert spec.upper_width == 0
    assert spec.lower_opacity == 1
    assert spec.upper_crease_length == 1


@pytest.mark.parametrize("field,value", [
    ("upper_width", -1), ("lower_width", -1),
    ("upper_opacity", -0.01), ("lower_opacity", 1.01),
    ("upper_crease_offset", -1), ("lower_crease_offset", -1),
    ("upper_crease_length", 0), ("lower_crease_length", 1.01),
    ("upper_crease_width", -1), ("lower_crease_width", -1),
    ("upper_crease_opacity", -0.01), ("lower_crease_opacity", 1.01),
])
def test_eyelid_existing_ranges_remain_enforced(field, value):
    with pytest.raises(ValueError):
        EyelidAppearance(**{field: value})


def test_eyelid_color_validation_remains_enforced():
    with pytest.raises(ValueError):
        EyelidAppearance(crease_color="not-a-color")
    with pytest.raises(ValueError):
        EyelidAppearance(upper_color="not-a-color")
    with pytest.raises(ValueError):
        EyelidAppearance(lower_color="not-a-color")


def test_eyelid_remains_frozen():
    spec = EyelidAppearance()
    with pytest.raises((AttributeError, TypeError)):
        spec.upper_width = 0.2

@pytest.mark.parametrize("value", [10**1000, -10**1000])
def test_eyelid_real_fields_reject_integer_overflow(value):
    with pytest.raises(ValueError):
        EyelidAppearance(upper_width=value)
