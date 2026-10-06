from __future__ import annotations

import hashlib

import pytest

from visual_engine.components.common.meta import Component, Parameter, VisualOverrides
from visual_engine.components.face.ear import generate_ear_geometry
from visual_engine.components.face.production_registry import production_face_geometry_registry
from visual_engine.entities import build_human_face
from visual_engine.math import Vec2
from visual_engine.persistence.serialization import component_payload, parameter_payload, component_from_payload
from visual_engine.runtime import ProductionRenderSession
from visual_engine.scene.composition import Camera, Placement


def _request(session: ProductionRenderSession):
    return session.render_face(
        "face-01", placement=Placement("face-01", Vec2(450.0, 450.0), scale=650.0), camera=Camera(),
        generator="face.human_with_eyes_nose_mouth_ears",
    )


def test_v156_explicit_ear_production_path_contains_two_real_ears():
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = session.render_face("face-01", placement=Placement("face-01", Vec2(450.0, 450.0), scale=650.0), camera=Camera(), generator="face.human_with_eyes_nose_mouth_ears")
    assert result.generator == "face.human_with_eyes_nose_mouth_ears"
    names = {surface.name for surface in result.camera_geometry.surfaces}
    assert {"left_ear:ear", "right_ear:ear"} <= names
    depths = {
        surface.name: int(surface.data["depth_layer"])
        for surface in result.camera_geometry.surfaces
        if surface.name in {"left_ear:ear", "right_ear:ear", "face:head:head"}
    }
    assert depths == {"left_ear:ear": 0, "right_ear:ear": 0, "face:head:head": 0}


def test_v156_ear_geometry_is_behind_head_without_renderer_special_case():
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _request(session)
    path_indices = {
        surface.name: int(surface.data["path_index"])
        for surface in result.camera_geometry.surfaces
        if surface.name in {"left_ear:ear", "right_ear:ear", "face:head:head"}
    }
    ordered = []
    for index, path in enumerate(result.camera_geometry.paths):
        text = " ".join(command + (" " + " ".join(f"{v:.6f}" for v in values) if values else "") for command, values in path.commands)
        ordered.append((text, index))
    for ear_name in ("left_ear:ear", "right_ear:ear"):
        assert result.svg.find(ordered[path_indices[ear_name]][0]) < result.svg.find(ordered[path_indices["face:head:head"]][0])


def test_v156_ear_parameter_mutation_changes_geometry_identity_and_svg():
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        first = _request(session)
        ear = root.find("left_ear")
        assert ear is not None
        ear.set_parameter(Parameter("width", 0.40, 0.10, 0.50))
        second = _request(session)
    assert first.geometry.key != second.geometry.key
    assert hashlib.sha256(first.svg.encode()).hexdigest() != hashlib.sha256(second.svg.encode()).hexdigest()


def test_v156_ear_visibility_zero_removes_only_ear_paint():
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        visible = _request(session)
        ear = root.find("left_ear")
        assert ear is not None
        ear.visual_overrides = VisualOverrides(visibility=0.0)
        hidden = _request(session)
    assert visible.svg != hidden.svg
    ear_surface = next(s for s in visible.camera_geometry.surfaces if s.name == "left_ear:ear")
    path = visible.camera_geometry.paths[int(ear_surface.data["path_index"])]
    path_d = " ".join(
        command + (" " + " ".join(f"{value:.6f}" for value in values) if values else "")
        for command, values in path.commands
    )
    assert path_d in visible.svg
    assert path_d not in hidden.svg


def test_v156_ear_generator_rejects_invalid_dimensions_and_inputs():
    root = build_human_face("face-01")
    ear = root.find("left_ear")
    assert ear is not None
    ear.set_parameter(Parameter("width", 0.10, 0.10, 0.50))
    ear.set_parameter(Parameter("height", 0.16, 0.16, 0.70))
    generate_ear_geometry(ear)
    with pytest.raises(TypeError, match="does not accept custom inputs"):
        generate_ear_geometry(ear, {})
    bad = type(ear)(ear.id, ear.kind, parameters=dict(ear.parameters))
    from types import SimpleNamespace
    bad.parameters["width"] = SimpleNamespace(value=-1.0)
    with pytest.raises(ValueError, match="must be positive"):
        generate_ear_geometry(bad)



def test_v156_composite_rejects_one_or_three_ears():
    root = build_human_face("face-01")
    root.children = [child for child in root.children if child.kind != "Ear"]
    with ProductionRenderSession(root) as session:
        with pytest.raises(ValueError, match="exactly two direct Ear"):
            _request(session)
    root = build_human_face("face-01")
    root.add_child(Component("third_ear", "Ear"))
    with ProductionRenderSession(root) as session:
        with pytest.raises(ValueError, match="exactly two direct Ear"):
            _request(session)


def test_v156_ear_persistence_round_trip_preserves_parameters_and_visual_contract():
    root = build_human_face("face-01")
    ear = root.find("left_ear")
    assert ear is not None
    payload = component_payload(ear, child_order=0)
    restored = component_from_payload(
        ear.id, ear.kind, ear.parent_id, parameter_payload(ear.parameters),
        {name: {"x": a.x, "y": a.y, "z": a.z} for name, a in ear.anchors.items()}, payload,
    )
    assert restored.parameters == ear.parameters
    assert restored.visual == ear.visual
    assert restored.anchors == ear.anchors


def test_v156_public_registry_contains_ear_and_composite():
    registry = production_face_geometry_registry()
    assert registry.get("face.ear").kinds == ("Ear",)
    assert registry.get("face.human_with_eyes_nose_mouth_ears").kinds == ("HumanFace",)


def test_v156_explicit_previous_mouth_generator_remains_available():
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = session.render_face(
            "face-01", placement=Placement("face-01", Vec2(450.0, 450.0), scale=650.0),
            camera=Camera(), generator="face.human_with_eyes_nose_mouth",
        )
    assert result.generator == "face.human_with_eyes_nose_mouth"
    assert not any(surface.name.startswith("left_ear:") for surface in result.camera_geometry.surfaces)
