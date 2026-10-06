import math

import pytest

from visual_engine.components.face.eyes.highlights.spec import ReflectionMark


@pytest.mark.parametrize("field", ["x", "y", "width", "height", "opacity", "rotation_deg"])
@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_reflection_numeric_fields_reject_non_finite(field, value):
    with pytest.raises(ValueError):
        ReflectionMark(**{field: value})


@pytest.mark.parametrize("field", ["x", "y", "width", "height", "opacity", "rotation_deg"])
@pytest.mark.parametrize("value", [True, False, "0.5"])
def test_reflection_numeric_fields_reject_bool_and_string(field, value):
    with pytest.raises(ValueError):
        ReflectionMark(**{field: value})


@pytest.mark.parametrize("field", ["x", "y", "width", "height", "opacity", "rotation_deg"])
def test_reflection_numeric_fields_reject_unrepresentable_huge_integer(field):
    with pytest.raises(ValueError):
        ReflectionMark(**{field: 10**10000})


@pytest.mark.parametrize("shape", ["circle", "ellipse", "diamond", "streak"])
def test_reflection_shape_vocabulary_is_closed(shape):
    mark = ReflectionMark(shape=shape)
    assert mark.shape == shape


@pytest.mark.parametrize("shape", ["triangle", "square", "", None, 1])
def test_reflection_shape_rejects_unknown_values(shape):
    with pytest.raises(ValueError):
        ReflectionMark(shape=shape)


@pytest.mark.parametrize("shape", [[], {}, object()])
def test_reflection_shape_rejects_unhashable_or_opaque_values(shape):
    with pytest.raises(ValueError):
        ReflectionMark(shape=shape)


@pytest.mark.parametrize("field,value", [("width", -0.001), ("height", -0.001), ("opacity", -0.001), ("opacity", 1.001)])
def test_existing_reflection_ranges_remain_enforced(field, value):
    with pytest.raises(ValueError):
        ReflectionMark(**{field: value})


def test_reflection_boundary_values_and_color_remain_valid():
    mark = ReflectionMark(
        shape="streak", x=-1.0, y=1.0, width=0.0, height=0.0,
        color="#AABBCCDD", opacity=0.0, rotation_deg=-360.0,
    )
    assert mark.width == 0.0
    assert mark.height == 0.0
    assert mark.opacity == 0.0
    assert mark.color == "#AABBCCDD"


def test_reflection_mark_remains_immutable():
    mark = ReflectionMark()
    with pytest.raises(AttributeError):
        mark.x = 1.0
