from __future__ import annotations

import hashlib

import pytest

from visual_engine.components.common.visual_contract import VisualContract
from visual_engine.entities import build_human_face
from visual_engine.math import Vec2
from visual_engine.runtime import ProductionRenderSession
from visual_engine.runtime.production_face_render import render_production_face
from visual_engine.scene.composition import Camera, Placement


def _request(session: ProductionRenderSession, generator: str = "face.human_with_eyes_nose_mouth_ears_hair"):
    return session.render_face(
        "face-01",
        placement=Placement("face-01", Vec2(450.0, 450.0), scale=650.0),
        camera=Camera(),
        generator=generator,
    )


def test_v167_face_render_owner_preserves_public_session_result() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _request(session)
    assert result.component_id == "face-01"
    assert result.generator.endswith("ears_hair")
    assert result.svg.startswith("<svg")
    assert hashlib.sha256(result.svg.encode()).hexdigest()
    assert result.geometry.geometry.surfaces


def test_v167_face_render_direct_owner_matches_session_path() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        session_result = _request(session)
        direct_result = render_production_face(
            root,
            session.graph,
            session._resources,
            session.resolution_cache,
            "face-01",
            placement=Placement("face-01", Vec2(450.0, 450.0), scale=650.0),
            camera=Camera(),
            generator="face.human_with_eyes_nose_mouth_ears_hair",
        )
    assert session_result.svg == direct_result.svg
    assert session_result.camera_geometry == direct_result.camera_geometry
    assert session_result.visibility == direct_result.visibility
    assert session_result.hair_ear_occlusion == direct_result.hair_ear_occlusion
    assert session_result.head_ear_occlusion == direct_result.head_ear_occlusion


def test_v167_face_render_rejects_invalid_owner_boundary() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        with pytest.raises(TypeError, match="root"):
            render_production_face(object(), session.graph, session._resources, session.resolution_cache, "face-01", generator="x")
        with pytest.raises(ValueError, match="component_id"):
            render_production_face(root, session.graph, session._resources, session.resolution_cache, "", generator="x")
        with pytest.raises(ValueError, match="generator"):
            render_production_face(root, session.graph, session._resources, session.resolution_cache, "face-01", generator="")


def test_v167_supported_generator_keeps_unproven_relations_empty() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _request(session, generator="face.human_with_eyes_nose")
    assert result.visibility is not None
    assert result.hair_ear_occlusion == ()
    assert result.head_ear_occlusion == ()


def test_v167_hidden_visual_remains_renderer_visible_contract_path() -> None:
    root = build_human_face("face-01")
    old = root.visual
    root.visual = VisualContract(
        fill_color=old.fill_color,
        contour=old.contour,
        material=old.material,
        opacity=old.opacity,
        visibility=0.0,
    )
    with ProductionRenderSession(root) as session:
        result = _request(session)
    assert result.svg.startswith("<svg")
