from __future__ import annotations

import gc
import hashlib

import pytest

from visual_engine.components.common.geometry_contract import GeometryContract, GeometryMask, GeometryPrimitive
from visual_engine.entities import build_human_face
from visual_engine.math import Vec2
from visual_engine.render import render_geometry_svg
from visual_engine.runtime import (
    ProductionRenderSession,
    ResolutionCache,
    VersionStamp,
)
from visual_engine.scene.composition import Camera, Placement


def _request(session: ProductionRenderSession):
    return session.render_face(
        "face-01",
        placement=Placement("face-01", Vec2(450.0, 450.0), scale=650.0),
        camera=Camera(),
        generator="face.human_with_eyes_nose",
    )


def test_v145_is_a_real_caller_owned_production_session() -> None:
    root = build_human_face("face-01")
    session = ProductionRenderSession(root)
    first = _request(session)
    second = _request(session)

    assert first.component_id == "face-01"
    assert first.generator == "face.human_with_eyes_nose"
    assert first.svg.startswith("<svg")
    assert first.svg == second.svg
    assert session.geometry_cache.stats().builds == 4  # two eyes + nose + composite face
    assert session.geometry_cache.stats().hits >= 3
    assert session.resolution_cache.stats.stores == 4  # face + two eyes + nose
    assert session.resolution_cache.stats.hits >= 3
    session.close()


def test_v145_render_is_deterministic_across_fresh_sessions() -> None:
    outputs = []
    for _ in range(2):
        root = build_human_face("face-01")
        with ProductionRenderSession(root) as session:
            outputs.append(_request(session).svg.encode("utf-8"))
    assert outputs[0] == outputs[1]
    assert hashlib.sha256(outputs[0]).hexdigest() == hashlib.sha256(outputs[1]).hexdigest()


def test_v145_stale_graph_fails_closed_until_refresh() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        _request(session)
        root.add_child(type(root)("unrendered.extra", "Ear"))
        with pytest.raises(RuntimeError, match="stale"):
            _request(session)
        session.refresh()
        refreshed = _request(session)
        assert refreshed.svg.startswith("<svg")


def test_v145_close_releases_session_owned_graph_and_caches() -> None:
    root = build_human_face("face-01")
    session = ProductionRenderSession(root)
    geometry_cache = session.geometry_cache
    resolution_cache = session.resolution_cache
    _request(session)
    session.close()
    assert geometry_cache.stats().entries == 0
    assert len(resolution_cache) == 0
    assert session._graph is None  # lifecycle boundary: graph no longer retained by session
    assert session._root is None
    del session
    del root
    gc.collect()


def test_v145_generic_svg_fails_closed_for_masks_and_unknown_primitives() -> None:
    with pytest.raises(ValueError, match="masks"):
        render_geometry_svg(GeometryContract(masks=(GeometryMask("x"),)))
    with pytest.raises(ValueError, match="primitive"):
        render_geometry_svg(GeometryContract(primitives=(GeometryPrimitive("triangle", {"x": 1}),)))


def test_v145_resolution_cache_is_explicitly_caller_owned() -> None:
    root = build_human_face("face-01")
    cache = ResolutionCache(max_entries=8)
    session = ProductionRenderSession(root, resolution_cache=cache)
    _request(session)
    assert session.resolution_cache is cache
    session.close()
    # Injected caches are caller-owned; V1.46 deliberately leaves them intact
    # so another live session can continue using the same cache.
    assert len(cache) == 4
    cache.clear()


def test_v145_composite_surface_indexes_are_global_and_owner_aware() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _request(session)
        surfaces = result.geometry.geometry.surfaces
        right_aperture = next(s for s in surfaces if s.name.endswith("right_eye:aperture"))
        head = next(s for s in surfaces if s.name == "head:head")
        assert right_aperture.data["path_index"] > 0
        assert right_aperture.data["source_component_id"] == "right_eye"
        assert head.data["source_component_id"] == "face-01"
