from __future__ import annotations

import ast
from pathlib import Path

import pytest

from visual_engine.components.common.meta import Component
from visual_engine.entities import build_human_face
from visual_engine.runtime import ProductionRenderSession as PublicSession
from visual_engine.runtime.production_render_session import ProductionRenderSession
from visual_engine.runtime.production_slice import ProductionRenderSession as CompatibilitySession
from visual_engine.runtime.geometry_cache import GeometryCache
from visual_engine.runtime.resolution_cache import ResolutionCache

ROOT = Path(__file__).resolve().parents[4]


def test_v171_owner_and_compatibility_identity() -> None:
    assert ProductionSessionSource().class_name == "ProductionRenderSession"
    assert CompatibilitySession is ProductionRenderSession
    assert PublicSession is ProductionRenderSession


def test_v171_owner_has_one_session_responsibility_and_no_duplicate_class() -> None:
    owner = ROOT / "src/visual_engine/runtime/production_render_session.py"
    facade = ROOT / "src/visual_engine/runtime/production_slice.py"
    tree = ast.parse(owner.read_text(encoding="utf-8"))
    classes = [node.name for node in tree.body if isinstance(node, ast.ClassDef)]
    assert classes == ["ProductionRenderSession"]
    assert "class ProductionRenderSession" not in facade.read_text(encoding="utf-8")
    assert len(owner.read_text(encoding="utf-8").splitlines()) <= 150


def test_v171_invalid_root_and_closed_session_fail_closed() -> None:
    with pytest.raises(TypeError, match="root"):
        ProductionRenderSession(object())  # type: ignore[arg-type]
    session = ProductionRenderSession(build_human_face("face-01"))
    session.close()
    session.close()
    with pytest.raises(RuntimeError, match="closed"):
        _ = session.graph
    with pytest.raises(RuntimeError, match="closed"):
        session.render_face("face-01")
    with pytest.raises(RuntimeError, match="closed"):
        session.refresh()


def test_v171_injected_caches_remain_caller_owned() -> None:
    root = build_human_face("face-01")
    geometry_cache = GeometryCache(max_entries=8)
    resolution_cache = ResolutionCache(max_entries=8)
    session = ProductionRenderSession(
        root, geometry_cache=geometry_cache, resolution_cache=resolution_cache
    )
    assert session.geometry_cache is geometry_cache
    assert session.resolution_cache is resolution_cache
    session.render_face("face-01")
    geometry_entries = geometry_cache.stats().entries
    resolution_entries = len(resolution_cache)
    assert geometry_entries > 0 and resolution_entries > 0
    session.close()
    assert geometry_cache.stats().entries == geometry_entries
    assert len(resolution_cache) == resolution_entries
    # Injected caches remain caller-owned after session teardown.
    geometry_cache.clear()
    resolution_cache.clear()


def test_v171_real_production_path_and_refresh_boundary() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        first = session.render_face("face-01")
        assert first.svg.startswith("<svg")
        root.add_child(Component("v171.extra", "Decor"))
        with pytest.raises(RuntimeError, match="stale"):
            session.render_face("face-01")
        session.refresh()
        second = session.render_face("face-01")
        assert second.svg.startswith("<svg")


class ProductionSessionSource:
    """Tiny test helper keeping the source-owner assertion explicit."""

    class_name = "ProductionRenderSession"
