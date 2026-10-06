from __future__ import annotations

import hashlib

import pytest

from visual_engine.components.common.visual_contract import VisualOverrides
from visual_engine.entities import build_human_face
from visual_engine.persistence.serialization import component_payload, parameter_payload, component_from_payload
from visual_engine.runtime import ProductionRenderSession
from visual_engine.components.face.production_registry import production_face_geometry_registry
from visual_engine.scene.composition import Camera, Placement
from visual_engine.math import Vec2


def _request(session):
    return session.render_face(
        "face-01", placement=Placement("face-01", Vec2(450.0, 450.0), scale=650.0),
        camera=Camera(), generator="face.human_with_eyes_nose_mouth",
    )


def test_v155_default_face_production_path_contains_mouth_and_two_real_occluders():
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _request(session)
    assert result.generator == "face.human_with_eyes_nose_mouth"
    assert any(surface.name == "mouth:mouth" for surface in result.camera_geometry.surfaces)
    assert result.visibility is not None
    assert result.visibility.occluder_ids == ("nose", "mouth")
    assert result.visibility.visibility.overall_coverage > 0.0
    assert {item.occluder_id for _, values in result.visibility.attribution.regions for item in values} == {"nose", "mouth"}


def test_v155_mouth_parameter_changes_geometry_cache_identity_and_svg():
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        first = _request(session)
        mouth = root.find("mouth")
        assert mouth is not None
        from visual_engine.components.common.meta import Parameter
        mouth.set_parameter(Parameter("width", 0.40, 0.08, 0.70))
        second = _request(session)
    assert first.geometry.key != second.geometry.key
    assert hashlib.sha256(first.svg.encode()).hexdigest() != hashlib.sha256(second.svg.encode()).hexdigest()


def test_v155_mouth_visibility_zero_removes_only_mouth_geometry():
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        visible = _request(session)
        mouth = root.find("mouth")
        assert mouth is not None
        mouth.visual_overrides = VisualOverrides(visibility=0.0)
        hidden = _request(session)
    assert visible.svg != hidden.svg
    assert "mouth:mouth" in [s.name for s in visible.camera_geometry.surfaces]
    assert "mouth:mouth" in [s.name for s in hidden.camera_geometry.surfaces]
    assert hidden.svg.count("#5b1f24") < visible.svg.count("#5b1f24")


def test_v155_composite_requires_exactly_one_mouth():
    root = build_human_face("face-01")
    root.children = [child for child in root.children if child.kind != "Mouth"]
    with ProductionRenderSession(root) as session:
        with pytest.raises(ValueError, match="exactly one Nose and one Mouth"):
            _request(session)


def test_v155_public_registry_contains_mouth_generator_and_explicit_composite():
    registry = production_face_geometry_registry()
    assert registry.get("face.mouth").kinds == ("Mouth",)
    assert registry.get("face.human_with_eyes_nose_mouth").kinds == ("HumanFace",)


def test_v155_generic_component_persistence_round_trip_preserves_mouth_contract():
    root = build_human_face("face-01")
    mouth = root.find("mouth")
    assert mouth is not None
    payload = component_payload(mouth, child_order=3)
    restored = component_from_payload(
        mouth.id,
        mouth.kind,
        mouth.parent_id,
        parameter_payload(mouth.parameters),
        {name: {"x": a.x, "y": a.y, "z": a.z} for name, a in mouth.anchors.items()},
        payload,
    )
    assert restored.id == "mouth"
    assert restored.kind == "Mouth"
    assert restored.parameters == mouth.parameters
    assert restored.visual == mouth.visual
    assert restored.anchors == mouth.anchors
