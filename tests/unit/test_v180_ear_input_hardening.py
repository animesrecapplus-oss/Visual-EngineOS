from __future__ import annotations

import math
from types import SimpleNamespace

import pytest

from visual_engine.components.common.meta import Component, Parameter
from visual_engine.components.face.ear import generate_ear_geometry
from visual_engine.entities import build_human_face


def _ear():
    root = build_human_face("face-01")
    ear = root.find("left_ear")
    assert ear is not None
    return ear


def test_v180_valid_numeric_parameters_keep_existing_geometry_contract():
    geometry = generate_ear_geometry(_ear())
    assert geometry.coordinate_frame == "component"
    assert len(geometry.paths) == 1
    assert geometry.surfaces[0].data["semantic_region"] == "EAR"
    assert geometry.surfaces[0].data["depth_layer"] == 0


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
@pytest.mark.parametrize("name", ["width", "height"])
def test_v180_non_finite_malformed_parameter_is_rejected(name, value):
    ear = _ear()
    ear.parameters[name] = SimpleNamespace(value=value)
    with pytest.raises(ValueError, match=f"ear {name} must be finite"):
        generate_ear_geometry(ear)


@pytest.mark.parametrize("value", ["0.2", object(), True])
@pytest.mark.parametrize("name", ["width", "height"])
def test_v180_non_numeric_malformed_parameter_is_rejected(name, value):
    ear = _ear()
    ear.parameters[name] = SimpleNamespace(value=value)
    with pytest.raises(TypeError, match=f"ear {name} must be numeric"):
        generate_ear_geometry(ear)


@pytest.mark.parametrize("name", ["width", "height"])
def test_v180_positive_subnormal_dimension_is_rejected_before_degenerate_path(name):
    ear = _ear()
    ear.parameters[name] = SimpleNamespace(value=5e-324)
    with pytest.raises(ValueError, match="below representable geometry precision"):
        generate_ear_geometry(ear)


def test_v180_normal_parameter_constructor_still_rejects_non_finite_values():
    with pytest.raises(ValueError, match="finite"):
        Parameter("width", math.nan, 0.1, 0.5)
