from __future__ import annotations

import math

import pytest

from visual_engine.components.common.visual_contract import VisualContract
from visual_engine.entities import build_human_face
from visual_engine.runtime import (
    ProductionRenderSession,
    resolve_production_head_ear_relations,
)
from visual_engine.runtime.production_owner_geometry import extract_production_owner_geometry
from visual_engine.scene.composition import Camera, Placement
from visual_engine.math import Vec2


def _render(session: ProductionRenderSession):
    return session.render_face(
        "face-01", placement=Placement("face-01", Vec2(450, 450), scale=650), camera=Camera()
    )


def test_v164_direct_relations_equal_session_result():
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _render(session)
        direct = resolve_production_head_ear_relations(
            root,
            result.camera_geometry,
            result.resolution.visual,
            owner_geometry=extract_production_owner_geometry,
        )
    assert direct == result.head_ear_occlusion


def test_v164_relation_preserves_hidden_head_optical_behavior():
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        visible = _render(session)
        old = root.visual
        root.visual = VisualContract(
            fill_color=old.fill_color, contour=old.contour, material=old.material,
            opacity=old.opacity, visibility=0.0,
        )
        hidden = _render(session)
    assert [item.coverage for item in hidden.head_ear_occlusion] == pytest.approx(
        [item.coverage for item in visible.head_ear_occlusion]
    )
    assert all(item.visible == pytest.approx(1.0) for item in hidden.head_ear_occlusion)


def test_v164_relation_rejects_missing_ear_and_invalid_boundaries():
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _render(session)
        with pytest.raises(TypeError, match="Component root"):
            resolve_production_head_ear_relations(object(), result.camera_geometry, result.resolution.visual, owner_geometry=extract_production_owner_geometry)
        with pytest.raises(TypeError, match="GeometryContract"):
            resolve_production_head_ear_relations(root, object(), result.resolution.visual, owner_geometry=extract_production_owner_geometry)
        with pytest.raises(TypeError, match="ResolvedVisualContract"):
            resolve_production_head_ear_relations(root, result.camera_geometry, object(), owner_geometry=extract_production_owner_geometry)
        with pytest.raises(TypeError, match="callable"):
            resolve_production_head_ear_relations(root, result.camera_geometry, result.resolution.visual, owner_geometry=object())
        root_without_ear = build_human_face("face-01")
        ear = root_without_ear.find("left_ear")
        assert ear is not None
        root_without_ear.children.remove(ear)
        with pytest.raises(ValueError, match="left_ear"):
            resolve_production_head_ear_relations(root_without_ear, result.camera_geometry, result.resolution.visual, owner_geometry=extract_production_owner_geometry)


def test_v164_relation_rejects_invalid_owner_geometry_results():
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _render(session)
        def bad_geometry(_geometry, owner_id):
            if owner_id == "face-01":
                return object(), 0.0
            return extract_production_owner_geometry(_geometry, owner_id)
        with pytest.raises(TypeError, match="GeometryContract"):
            resolve_production_head_ear_relations(root, result.camera_geometry, result.resolution.visual, owner_geometry=bad_geometry)

        def bad_depth(_geometry, owner_id):
            if owner_id == "face-01":
                return extract_production_owner_geometry(_geometry, owner_id)[0], math.nan
            return extract_production_owner_geometry(_geometry, owner_id)
        with pytest.raises(ValueError, match="finite"):
            resolve_production_head_ear_relations(root, result.camera_geometry, result.resolution.visual, owner_geometry=bad_depth)


def test_v164_relation_preserves_stable_owner_geometry_order():
    root = build_human_face("face-01")
    calls: list[str] = []
    with ProductionRenderSession(root) as session:
        result = _render(session)
        def owner_geometry(geometry, owner_id):
            calls.append(owner_id)
            return extract_production_owner_geometry(geometry, owner_id)
        direct = resolve_production_head_ear_relations(
            root, result.camera_geometry, result.resolution.visual, owner_geometry=owner_geometry
        )
    assert [item.ear_id for item in direct] == ["left_ear", "right_ear"]
    assert calls == ["face-01", "left_ear", "right_ear"]
