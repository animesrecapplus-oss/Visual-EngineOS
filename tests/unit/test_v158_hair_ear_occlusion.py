from __future__ import annotations

import math

import pytest

from visual_engine.components.common.meta import VisualOverrides
from visual_engine.components.face.hair import generate_hair_geometry
from visual_engine.entities import build_human_face
from visual_engine.runtime import ProductionRenderSession, resolve_hair_ear_occlusion
from visual_engine.scene.composition import Camera, Placement
from visual_engine.math import Vec2


def _request(session):
    return session.render_face(
        "face-01", placement=Placement("face-01", Vec2(450, 450), scale=650), camera=Camera()
    )


def test_v158_real_hair_ear_overlap_is_resolved_for_both_ears():
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _request(session)
    assert len(result.hair_ear_occlusion) == 2
    assert {item.ear_id for item in result.hair_ear_occlusion} == {"left_ear", "right_ear"}
    assert all(item.hair_id == "hair" for item in result.hair_ear_occlusion)
    assert all(0.0 < item.coverage < 1.0 for item in result.hair_ear_occlusion)
    assert all(0.0 < item.visible < 1.0 for item in result.hair_ear_occlusion)
    assert all(item.depth_relation.value == "front" for item in result.hair_ear_occlusion)
    assert all(item.hair_depth == 1.0 and item.ear_depth == 0.0 for item in result.hair_ear_occlusion)
    assert int(next(s.data["depth_layer"] for s in result.camera_geometry.surfaces if s.name == "hair:hair")) == 1


def test_v158_hair_hidden_removes_optical_occlusion_but_preserves_geometric_overlap():
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        visible = _request(session)
        hair = root.find("hair")
        assert hair is not None
        hair.visual_overrides = VisualOverrides(visibility=0.0)
        hidden = _request(session)
    assert all(item.coverage > 0.0 for item in hidden.hair_ear_occlusion)
    assert all(item.visible == pytest.approx(1.0) for item in hidden.hair_ear_occlusion)
    assert all(item.coverage == pytest.approx(v.coverage) for item, v in zip(hidden.hair_ear_occlusion, visible.hair_ear_occlusion))


def test_v158_transmission_and_opacity_are_forwarded_to_generic_kernel():
    root = build_human_face("face-01")
    ear = root.find("left_ear")
    hair = root.find("hair")
    assert ear is not None and hair is not None
    from visual_engine.components.face.ear import generate_ear_geometry
    from visual_engine.components.face.hair import generate_hair_geometry
    result = resolve_hair_ear_occlusion(
        ear, generate_ear_geometry(ear), 0.0, hair, generate_hair_geometry(hair), 1.0,
        hair_opacity=0.5, hair_transmission=0.25,
    )
    assert result.visibility.overall_visible < 1.0
    assert result.visibility.overall_visible > 0.5


def test_v158_adapter_rejects_wrong_component_kinds_and_invalid_scalar_inputs():
    root = build_human_face("face-01")
    ear = root.find("left_ear")
    hair = root.find("hair")
    assert ear is not None and hair is not None
    eg = generate_hair_geometry(hair)
    with pytest.raises(ValueError, match="requires Ear then Hair"):
        resolve_hair_ear_occlusion(hair, eg, 0.0, ear, eg, 1.0)
    from visual_engine.components.face.ear import generate_ear_geometry
    ear_geometry = generate_ear_geometry(ear)
    with pytest.raises(ValueError, match="finite"):
        resolve_hair_ear_occlusion(ear, ear_geometry, math.nan, hair, eg, 1.0)
    with pytest.raises(ValueError, match=r"\[0,1\]"):
        resolve_hair_ear_occlusion(ear, ear_geometry, 0.0, hair, eg, 1.0, hair_opacity=2.0)


def test_v158_adapter_rejects_same_owner_and_invalid_region_output():
    root = build_human_face("face-01")
    hair = root.find("hair")
    assert hair is not None
    with pytest.raises(ValueError, match="distinct"):
        resolve_hair_ear_occlusion(hair, generate_hair_geometry(hair), 0.0, hair, generate_hair_geometry(hair), 1.0)


def test_v158_public_export_and_previous_generator_compatibility():
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        previous = session.render_face(
            "face-01", placement=Placement("face-01", Vec2(450, 450), scale=650), camera=Camera(),
            generator="face.human_with_eyes_nose_mouth_ears",
        )
    assert previous.hair_ear_occlusion == ()
    assert callable(resolve_hair_ear_occlusion)
