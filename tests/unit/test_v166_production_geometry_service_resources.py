from __future__ import annotations

import pytest

from visual_engine.entities import build_human_face
from visual_engine.runtime import GeometryCache, ProductionRenderSession, ResolutionCache
from visual_engine.runtime.production_geometry_service_resources import ProductionGeometryServiceResources


def test_v166_service_resources_release_only_registry_and_service() -> None:
    cache = GeometryCache(max_entries=8)
    resources = ProductionGeometryServiceResources(cache)
    assert resources.geometry_service is not None
    resources.close()
    assert resources._closed is True
    assert cache.stats().entries == 0
    with pytest.raises(RuntimeError, match="closed"):
        _ = resources.geometry_service
    resources.close()


def test_v166_service_resources_reject_invalid_cache_boundary() -> None:
    with pytest.raises(TypeError, match="geometry_cache"):
        ProductionGeometryServiceResources(object())  # type: ignore[arg-type]


def test_v166_session_remains_canonical_cache_owner() -> None:
    root = build_human_face("face-01")
    geometry_cache = GeometryCache(max_entries=16)
    resolution_cache = ResolutionCache(max_entries=16)
    with ProductionRenderSession(root, geometry_cache=geometry_cache, resolution_cache=resolution_cache) as session:
        assert session.geometry_cache is geometry_cache
        assert session.resolution_cache is resolution_cache
        assert session.render_face("face-01").svg.startswith("<svg")
    assert geometry_cache.stats().entries > 0
    assert len(resolution_cache) > 0


def test_v166_session_created_caches_still_clear_on_close() -> None:
    root = build_human_face("face-01")
    session = ProductionRenderSession(root)
    session.render_face("face-01")
    geometry_cache = session.geometry_cache
    resolution_cache = session.resolution_cache
    session.close()
    assert geometry_cache.stats().entries == 0
    assert len(resolution_cache) == 0
