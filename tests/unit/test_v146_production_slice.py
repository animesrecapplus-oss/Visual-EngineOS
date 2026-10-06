from __future__ import annotations

import hashlib
from concurrent.futures import ThreadPoolExecutor

import pytest

from visual_engine.components.common.visual_contract import VisualOverrides
from visual_engine.entities import build_human_face
from visual_engine.math import Vec2
from visual_engine.render import render_geometry_svg
from visual_engine.runtime import (
    GeometryCache,
    ProductionRenderSession,
    ResolutionCache,
    ResolutionContext,
    resolve_component,
)
from visual_engine.components.common.geometry_contract import GeometryContract, GeometryMask, GeometryPrimitive
from visual_engine.scene.composition import Camera, Placement


def _request(session: ProductionRenderSession, component_id: str = "face-01"):
    return session.render_face(
        component_id,
        placement=Placement(component_id, Vec2(450.0, 450.0), scale=650.0),
        camera=Camera(),
        generator="face.human_with_eyes_nose",
    )


def test_v146_adds_exactly_one_real_human_face_family_nose() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _request(session)
        assert result.generator == "face.human_with_eyes_nose"
        assert any(surface.name == "nose:nose" for surface in result.geometry.geometry.surfaces)
        assert session.geometry_cache.stats().builds == 4
        assert session.resolution_cache.stats.stores == 4


def test_v146_shared_cache_is_thread_safe_across_live_sessions() -> None:
    geometry_cache = GeometryCache(max_entries=16)
    resolution_cache = ResolutionCache(max_entries=16)
    sessions = [
        ProductionRenderSession(build_human_face("face-01"), geometry_cache=geometry_cache, resolution_cache=resolution_cache),
        ProductionRenderSession(build_human_face("face-01"), geometry_cache=geometry_cache, resolution_cache=resolution_cache),
    ]
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(_request, sessions))
        assert all(result.svg.startswith("<svg") for result in results)
        assert geometry_cache.stats().builds == 4
        assert resolution_cache.stats.stores == 4
    finally:
        for session in sessions:
            session.close()
        geometry_cache.clear()
        resolution_cache.clear()


def test_v146_nose_generator_rejects_missing_or_duplicated_nose_topology() -> None:
    root = build_human_face("face-01")
    nose = root.find("nose")
    assert nose is not None
    root.children.remove(nose)
    with ProductionRenderSession(root) as session:
        with pytest.raises(ValueError, match="exactly one direct Nose"):
            _request(session)


def test_v146_nose_geometry_contract_is_closed_and_renderer_neutral() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _request(session)
        nose_surfaces = [s for s in result.geometry.geometry.surfaces if s.name.startswith("nose:")]
        assert len(nose_surfaces) == 3
        nose_paths = [result.geometry.geometry.paths[int(s.data["path_index"])] for s in nose_surfaces]
        assert nose_paths[0].commands[-1][0] == "Z"
        assert all(path.commands for path in nose_paths)
        assert result.geometry.geometry.masks == ()


def test_v146_nose_uses_generic_visual_inheritance() -> None:
    root = build_human_face("face-01")
    nose = root.find("nose")
    assert nose is not None
    assert isinstance(nose.visual_overrides, VisualOverrides)
    with ProductionRenderSession(root) as session:
        face = resolve_component(session.graph, "face-01", cache=session.resolution_cache)
        resolved_nose = resolve_component(session.graph, "nose", cache=session.resolution_cache)
        assert resolved_nose.visual.effective_fill_color == face.visual.effective_fill_color
        assert resolved_nose.visual.effective_contour.color == face.visual.effective_contour.color


def test_v146_shared_injected_caches_survive_one_session_close() -> None:
    geometry_cache = GeometryCache(max_entries=32)
    resolution_cache = ResolutionCache(max_entries=32)
    first = ProductionRenderSession(build_human_face("face-01"), geometry_cache=geometry_cache, resolution_cache=resolution_cache)
    second = ProductionRenderSession(build_human_face("face-01"), geometry_cache=geometry_cache, resolution_cache=resolution_cache)
    _request(first)
    before = (geometry_cache.stats().builds, resolution_cache.stats.stores)
    _request(second)
    reused = (geometry_cache.stats().hits, resolution_cache.stats.hits)
    first.close()
    assert geometry_cache.stats().entries == 4
    assert len(resolution_cache) == 4
    _request(second)
    assert geometry_cache.stats().builds == before[0]
    assert resolution_cache.stats.stores == before[1]
    assert reused[0] > 0 and reused[1] > 0
    second.close()
    assert geometry_cache.stats().entries == 4
    assert len(resolution_cache) == 4
    geometry_cache.clear()
    resolution_cache.clear()


def test_v146_default_session_still_clears_its_owned_caches() -> None:
    session = ProductionRenderSession(build_human_face("face-01"))
    _request(session)
    geometry_cache = session.geometry_cache
    resolution_cache = session.resolution_cache
    session.close()
    assert geometry_cache.stats().entries == 0
    assert len(resolution_cache) == 0


def test_v146_visibility_zero_is_honored_by_the_production_renderer() -> None:
    root = build_human_face("face-01")
    left_eye = root.find("left_eye")
    assert left_eye is not None
    with ProductionRenderSession(root) as session:
        visible = _request(session)
        assert visible.svg.count("<ellipse") == 6
        left_eye.visual_overrides = VisualOverrides(visibility=0.0)
        hidden = _request(session)
        assert hidden.svg.count("<ellipse") == 3


def test_v146_root_visibility_zero_hides_all_owned_geometry() -> None:
    root = build_human_face("face-01")
    root.visual = type(root.visual)(
        fill_color=root.visual.fill_color,
        contour=root.visual.contour,
        material=root.visual.material,
        opacity=root.visual.opacity,
        visibility=0.0,
    )
    with ProductionRenderSession(root) as session:
        result = _request(session)
        assert result.svg.count("<ellipse") == 0
        assert result.svg.count("<path") == 0


def test_v146_nose_parameter_change_changes_geometry_identity_without_topology_refresh() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        first = _request(session)
        nose = root.find("nose")
        assert nose is not None
        nose.set_parameter(type(next(iter(nose.parameters.values())))("width", 0.16, 0.04, 0.30))
        second = _request(session)
        assert first.geometry.key != second.geometry.key
        assert second.geometry.cache_hit is False
        assert hashlib.sha256(first.svg.encode()).hexdigest() != hashlib.sha256(second.svg.encode()).hexdigest()


def test_v146_generic_renderer_still_fails_closed_for_unsupported_geometry() -> None:
    with pytest.raises(ValueError, match="masks"):
        render_geometry_svg(GeometryContract(masks=(GeometryMask("x"),)))
    with pytest.raises(ValueError, match="primitive"):
        render_geometry_svg(GeometryContract(primitives=(GeometryPrimitive("triangle", {"x": 1}),)))
