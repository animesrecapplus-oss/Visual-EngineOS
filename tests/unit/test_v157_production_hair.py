from __future__ import annotations

import hashlib

import pytest

from visual_engine.components.common.meta import Component, Parameter, VisualOverrides
from visual_engine.components.face.hair import generate_hair_geometry
from visual_engine.components.face.production_registry import production_face_geometry_registry
from visual_engine.entities import build_human_face
from visual_engine.math import Vec2
from visual_engine.persistence.serialization import component_from_payload, component_payload, parameter_payload
from visual_engine.runtime import ProductionRenderSession
from visual_engine.scene.composition import Camera, Placement


def _request(session: ProductionRenderSession, generator: str | None = None):
    kwargs = {} if generator is None else {"generator": generator}
    return session.render_face("face-01", placement=Placement("face-01", Vec2(450, 450), scale=650), camera=Camera(), **kwargs)


def test_v157_default_production_path_contains_one_real_hair():
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _request(session)
    assert result.generator == "face.human_with_eyes_nose_mouth_ears_hair"
    assert [s.name for s in result.camera_geometry.surfaces if s.name == "hair:hair"] == ["hair:hair"]


def test_v157_hair_is_painted_after_head_but_before_face_details():
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _request(session)
    roles = {s.name: s.data.get("path_index") for s in result.camera_geometry.surfaces}
    hair = roles["hair:hair"]
    head = roles["face:face:head:head"]
    nose = roles["face:face:nose:nose"]
    assert result.svg.find(_path_text(result, hair)) > result.svg.find(_path_text(result, head))
    assert result.svg.find(_path_text(result, hair)) < result.svg.find(_path_text(result, nose))
    assert result.svg.find(_path_text(result, hair)) < result.svg.find("<ellipse ")


def _path_text(result, index):
    path = result.camera_geometry.paths[int(index)]
    return " ".join(command + (" " + " ".join(f"{v:.6f}" for v in values) if values else "") for command, values in path.commands)


def test_v157_hair_parameter_mutation_changes_geometry_identity_and_svg():
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        first = _request(session)
        hair = root.find("hair")
        assert hair is not None
        hair.set_parameter(Parameter("width", 1.30, 0.60, 1.50))
        second = _request(session)
    assert first.geometry.key != second.geometry.key
    assert hashlib.sha256(first.svg.encode()).hexdigest() != hashlib.sha256(second.svg.encode()).hexdigest()


def test_v157_hair_visibility_zero_removes_only_hair_paint():
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        visible = _request(session)
        hair = root.find("hair")
        assert hair is not None
        hair.visual_overrides = VisualOverrides(visibility=0.0)
        hidden = _request(session)
    assert visible.svg != hidden.svg
    path = _path_text(visible, next(s.data["path_index"] for s in visible.camera_geometry.surfaces if s.name == "hair:hair"))
    assert path in visible.svg
    assert path not in hidden.svg


def test_v157_hair_generator_rejects_invalid_dimensions_and_inputs():
    root = build_human_face("face-01")
    hair = root.find("hair")
    assert hair is not None
    with pytest.raises(TypeError, match="does not accept custom inputs"):
        generate_hair_geometry(hair, {})
    bad = type(hair)(hair.id, hair.kind, parameters=dict(hair.parameters))
    bad.parameters["width"] = type("P", (), {"value": -1.0})()
    with pytest.raises(ValueError, match="must be positive"):
        generate_hair_geometry(bad)
    bad.parameters["width"] = type("P", (), {"value": float("nan")})()
    with pytest.raises(ValueError, match="must be positive"):
        generate_hair_geometry(bad)


def test_v157_composite_rejects_zero_or_two_hair_children():
    root = build_human_face("face-01")
    root.children = [child for child in root.children if child.kind != "Hair"]
    with ProductionRenderSession(root) as session:
        with pytest.raises(ValueError, match="exactly one direct Hair"):
            _request(session)
    root = build_human_face("face-01")
    root.add_child(Component("second_hair", "Hair"))
    with ProductionRenderSession(root) as session:
        with pytest.raises(ValueError, match="exactly one direct Hair"):
            _request(session)


def test_v157_hair_persistence_round_trip_preserves_contract():
    root = build_human_face("face-01")
    hair = root.find("hair")
    assert hair is not None
    payload = component_payload(hair, child_order=0)
    restored = component_from_payload(
        hair.id, hair.kind, hair.parent_id, parameter_payload(hair.parameters),
        {name: {"x": a.x, "y": a.y, "z": a.z} for name, a in hair.anchors.items()}, payload,
    )
    assert restored.parameters == hair.parameters
    assert restored.visual == hair.visual
    assert restored.anchors == hair.anchors


def test_v157_public_registry_contains_hair_and_composite():
    registry = production_face_geometry_registry()
    assert registry.get("face.hair").kinds == ("Hair",)
    assert registry.get("face.human_with_eyes_nose_mouth_ears_hair").kinds == ("HumanFace",)


def test_v157_previous_ear_generator_remains_available():
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _request(session, "face.human_with_eyes_nose_mouth_ears")
    assert result.generator == "face.human_with_eyes_nose_mouth_ears"
    assert not any(s.name == "hair:hair" for s in result.camera_geometry.surfaces)
