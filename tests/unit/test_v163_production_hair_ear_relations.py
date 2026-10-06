from __future__ import annotations

import pytest

from visual_engine.components.common.geometry_contract import GeometryContract
from visual_engine.components.common.meta import VisualOverrides
from visual_engine.entities import build_human_face
from visual_engine.runtime import ProductionRenderSession, resolve_production_hair_ear_relations
from visual_engine.runtime.contract import resolve_component
from visual_engine.runtime.production_owner_geometry import extract_production_owner_geometry
from visual_engine.scene.composition import Camera, Placement
from visual_engine.math import Vec2


def _render(session):
    return session.render_face(
        "face-01", placement=Placement("face-01", Vec2(450, 450), scale=650), camera=Camera()
    )


def test_v163_direct_relations_equal_session_result():
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _render(session)
        hair_visual = resolve_component(session.graph, "hair", cache=session.resolution_cache).visual
        direct = resolve_production_hair_ear_relations(
            root, result.camera_geometry, {"hair": hair_visual}
        )
    assert direct == result.hair_ear_occlusion


def test_v163_relation_preserves_hidden_hair_optical_behavior():
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        hair = root.find("hair")
        assert hair is not None
        hair.visual_overrides = VisualOverrides(visibility=0.0)
        result = _render(session)
    assert len(result.hair_ear_occlusion) == 2
    assert all(item.coverage > 0.0 and item.visible == pytest.approx(1.0) for item in result.hair_ear_occlusion)


def test_v163_relation_rejects_missing_hair_and_ear_and_style():
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _render(session)
        styles = {"face-01": result.resolution.visual}
        with pytest.raises(ValueError, match="Hair child"):
            root_without_hair = build_human_face("face-01")
            hair = root_without_hair.find("hair")
            assert hair is not None
            root_without_hair.children.remove(hair)
            resolve_production_hair_ear_relations(root_without_hair, result.camera_geometry, styles)
        with pytest.raises(ValueError, match="resolved style"):
            resolve_production_hair_ear_relations(root, result.camera_geometry, styles)
        with pytest.raises(ValueError, match="Ear production"):
            root_without_ear = build_human_face("face-01")
            ear = root_without_ear.find("left_ear")
            assert ear is not None
            root_without_ear.children.remove(ear)
            resolve_production_hair_ear_relations(root_without_ear, result.camera_geometry, {"hair": result.resolution.visual})


def test_v163_relation_rejects_invalid_boundary_types():
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _render(session)
        styles = {"hair": result.resolution.visual}
        with pytest.raises(TypeError, match="Component root"):
            resolve_production_hair_ear_relations(object(), result.camera_geometry, styles)
        with pytest.raises(TypeError, match="GeometryContract"):
            resolve_production_hair_ear_relations(root, object(), styles)
        with pytest.raises(TypeError, match="style mapping"):
            resolve_production_hair_ear_relations(root, result.camera_geometry, object())
        with pytest.raises(TypeError, match="callable"):
            resolve_production_hair_ear_relations(root, result.camera_geometry, styles, owner_geometry=object())


def test_v163_relation_preserves_stable_ear_order_and_owner_geometry_calls():
    root = build_human_face("face-01")
    calls = []
    with ProductionRenderSession(root) as session:
        result = _render(session)
        styles = {"hair": resolve_component(session.graph, "hair", cache=session.resolution_cache).visual}
        def owner_geometry(geometry, owner_id):
            calls.append(owner_id)
            return extract_production_owner_geometry(geometry, owner_id)
        direct = resolve_production_hair_ear_relations(root, result.camera_geometry, styles, owner_geometry=owner_geometry)
    assert [item.ear_id for item in direct] == ["left_ear", "right_ear"]
    assert calls == ["hair", "left_ear", "right_ear"]
