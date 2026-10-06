from __future__ import annotations

import pytest

from visual_engine.components.common.meta import Component, Parameter
from visual_engine.components.face.mouth import generate_mouth_geometry


def _bypassed_parameter(name: str, value):
    parameter = object.__new__(Parameter)
    object.__setattr__(parameter, "name", name)
    object.__setattr__(parameter, "value", value)
    object.__setattr__(parameter, "min_value", None)
    object.__setattr__(parameter, "max_value", None)
    return parameter


def _mouth_with_width(value) -> Component:
    mouth = Component("mouth-malformed", "Mouth")
    mouth.parameters["width"] = _bypassed_parameter("width", value)
    mouth.parameters["height"] = _bypassed_parameter("height", 0.08)
    return mouth


def test_mouth_rejects_bypassed_bool_and_string_width():
    for value in (True, "0.2"):
        with pytest.raises(TypeError, match="must be numeric"):
            generate_mouth_geometry(_mouth_with_width(value))


def test_mouth_rejects_bypassed_nonfinite_width():
    for value in (float("nan"), float("inf"), -float("inf")):
        with pytest.raises(ValueError, match="must be finite"):
            generate_mouth_geometry(_mouth_with_width(value))


def test_mouth_rejects_bypassed_nonpositive_width():
    for value in (0.0, -0.2):
        with pytest.raises(ValueError, match="must be positive"):
            generate_mouth_geometry(_mouth_with_width(value))


def test_mouth_rejects_positive_subnormal_zero_radius():
    with pytest.raises(ValueError, match="representable geometry precision"):
        generate_mouth_geometry(_mouth_with_width(5e-324))
