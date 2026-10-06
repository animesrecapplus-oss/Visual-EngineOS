from __future__ import annotations

import math

import pytest

from visual_engine.components.face.mouth import generate_mouth_geometry, mouth_geometry_generator
from visual_engine.entities import build_human_face
from visual_engine.components.common.meta import Component, Parameter


def test_mouth_geometry_is_finite_and_semantically_labelled():
    mouth = build_human_face().find("mouth")
    assert mouth is not None
    geometry = generate_mouth_geometry(mouth)
    primitive = geometry.primitives[0]
    assert primitive.kind == "ellipse"
    assert primitive.data["semantic_region"] == "MOUTH"
    assert primitive.data["component_id"] == "mouth"
    assert geometry.surfaces[0].data["depth_layer"] == 1
    assert all(math.isfinite(float(v)) for v in (primitive.data["cx"], primitive.data["cy"], primitive.data["rx"], primitive.data["ry"]))


def test_mouth_generator_rejects_custom_inputs_and_invalid_size():
    mouth = build_human_face().find("mouth")
    assert mouth is not None
    with pytest.raises(TypeError, match="custom inputs"):
        generate_mouth_geometry(mouth, object())
    with pytest.raises(ValueError, match="below minimum"):
        mouth.set_parameter(Parameter("width", 0.0, 0.08, 0.70))


def test_mouth_registered_generator_has_one_owner_and_no_custom_inputs():
    generator = mouth_geometry_generator()
    assert generator.name == "face.mouth"
    assert generator.version == "1"
    assert generator.kinds == ("Mouth",)

