from __future__ import annotations

import math

import pytest

from visual_engine.components.common.geometry_contract import GeometryContract
from visual_engine.entities import build_human_face
from visual_engine.math import Vec2
from visual_engine.runtime import (
    ProductionRenderSession,
    ResolutionContext,
    resolve_component,
    resolve_production_visual_styles,
)
from visual_engine.scene.composition import Camera, Placement


def _request(session: ProductionRenderSession):
    return session.render_face(
        "face-01", placement=Placement("face-01", Vec2(450.0, 450.0), scale=650.0),
        camera=Camera(), generator="face.human_with_eyes_nose_mouth_ears_hair",
    )


def test_v161_extracted_style_map_matches_canonical_resolution() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _request(session)
        direct = resolve_production_visual_styles(
            session.graph, "face-01", result.camera_geometry, result.resolution.visual,
            context=ResolutionContext(), cache=session.resolution_cache,
        )
        expected = {"face-01": result.resolution.visual}
        for owner_id in ("hair", "left_ear", "left_eye", "mouth", "nose", "right_ear", "right_eye"):
            expected[owner_id] = resolve_component(
                session.graph, owner_id, context=ResolutionContext(), cache=session.resolution_cache,
            ).visual
    assert direct == expected


def test_v161_production_render_does_not_duplicate_root_resolution() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        _request(session)
        assert session.resolution_cache.stats.stores == 8


def test_v161_unknown_geometry_owner_is_ignored_as_before() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _request(session)
        geometry = GeometryContract(
            coordinate_frame=result.camera_geometry.coordinate_frame,
            bounds=result.camera_geometry.bounds,
            primitives=result.camera_geometry.primitives,
            paths=result.camera_geometry.paths,
            surfaces=result.camera_geometry.surfaces + (
                type(result.camera_geometry.surfaces[0])(
                    "unknown", {"source_component_id": "ghost"}
                ),
            ),
            local_z=result.camera_geometry.local_z,
        )
        styles = resolve_production_visual_styles(
            session.graph, "face-01", geometry, result.resolution.visual,
            context=ResolutionContext(), cache=session.resolution_cache,
        )
    assert "ghost" not in styles


def test_v161_invalid_api_inputs_fail_closed() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _request(session)
        valid = result.resolution.visual
        with pytest.raises(TypeError, match="RuntimeGraph"):
            resolve_production_visual_styles(object(), "face-01", result.camera_geometry, valid)  # type: ignore[arg-type]
        with pytest.raises(ValueError, match="non-empty"):
            resolve_production_visual_styles(session.graph, "", result.camera_geometry, valid)
        with pytest.raises(TypeError, match="GeometryContract"):
            resolve_production_visual_styles(session.graph, "face-01", object(), valid)  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="ResolvedVisualContract"):
            resolve_production_visual_styles(session.graph, "face-01", result.camera_geometry, object())  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="ResolutionContext"):
            resolve_production_visual_styles(
                session.graph, "face-01", result.camera_geometry, valid, context=object()  # type: ignore[arg-type]
            )


def test_v161_style_resolution_remains_deterministic_for_same_inputs() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _request(session)
        first = resolve_production_visual_styles(
            session.graph, "face-01", result.camera_geometry, result.resolution.visual,
        )
        second = resolve_production_visual_styles(
            session.graph, "face-01", result.camera_geometry, result.resolution.visual,
        )
    assert tuple(first) == tuple(second)
    assert first == second


def test_v161_no_numeric_input_is_reinterpreted_by_style_adapter() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _request(session)
        assert math.isfinite(result.resolution.visual.opacity)
        assert math.isfinite(result.resolution.visual.effective_visibility)


def test_v161_context_change_reaches_generic_resolution_and_cache_identity() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _request(session)
        base = resolve_production_visual_styles(
            session.graph, "face-01", result.camera_geometry, result.resolution.visual,
            context=ResolutionContext(), cache=session.resolution_cache,
        )
        shadowed = resolve_production_visual_styles(
            session.graph, "face-01", result.camera_geometry, result.resolution.visual,
            context=ResolutionContext(shadow_alpha=0.25), cache=session.resolution_cache,
        )
    assert base["mouth"].shadow_alpha == 0.0
    assert shadowed["mouth"].shadow_alpha == 0.25
