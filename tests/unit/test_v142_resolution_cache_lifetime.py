from __future__ import annotations

import ast
import gc
from pathlib import Path

from visual_engine.components.common.meta import Component
from visual_engine.model import VisualContract
from visual_engine.runtime.contract import resolve_component
from visual_engine.runtime.graph import RuntimeGraph
from visual_engine.runtime.resolution_cache import ResolutionCache

ROOT = Path(__file__).resolve().parents[2]


def _tree(count: int, *, fill: str = "#406080") -> Component:
    root = Component("root", "scene-root", visual=VisualContract(fill_color=fill))
    for i in range(1, count):
        root.add_child(Component(f"node-{i:05d}", "node"))
    return root


def test_v142_cache_lifetime_claim_is_superseded_by_v145_owner_and_v161_style_owner():
    production = ROOT / "src"
    instantiations: list[tuple[str, int]] = []
    resolver_calls: list[tuple[str, int]] = []
    for path in production.rglob("*.py"):
        if path.as_posix().endswith("runtime/contract.py"):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "ResolutionCache":
                instantiations.append((str(path.relative_to(ROOT)), node.lineno))
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"resolve_component", "resolve_component_contract"}:
                resolver_calls.append((str(path.relative_to(ROOT)), node.lineno))
    assert all(path == "src/visual_engine/runtime/production_render_session.py" for path, _ in instantiations)
    assert {path for path, _ in resolver_calls} == {
        "src/visual_engine/runtime/production_face_render.py",
        "src/visual_engine/runtime/production_visual_styles.py",
    }
    assert instantiations and resolver_calls


def test_cache_result_does_not_keep_authoring_scene_alive():
    root = Component("teardown-unique-root", "scene-root", visual=VisualContract(fill_color="#406080"))
    root.add_child(Component("teardown-node", "node"))
    graph = RuntimeGraph.from_component(root)
    cache = ResolutionCache(max_entries=16)
    result = resolve_component(graph, "teardown-node", cache=cache)
    del result, graph, root
    gc.collect()
    retained = [obj for obj in gc.get_objects() if isinstance(obj, Component) and obj.id == "teardown-unique-root"]
    assert not retained
    assert len(cache) == 1


def test_shared_cache_can_reuse_exact_identity_across_independent_rebuilt_graphs():
    first = RuntimeGraph.from_component(_tree(32))
    second = RuntimeGraph.from_component(_tree(32))
    assert first is not second
    cache = ResolutionCache(max_entries=64)
    first_values = [resolve_component(first, node.id, cache=cache) for node in first.nodes.values()]
    stats_after_first = cache.stats
    second_values = [resolve_component(second, node.id, cache=cache) for node in second.nodes.values()]
    stats_after_second = cache.stats
    assert stats_after_first.misses == 32
    assert stats_after_second.hits - stats_after_first.hits == 32
    assert all(a is b for a, b in zip(first_values, second_values))


def test_partitioned_caches_do_not_share_even_when_identity_is_exact():
    first = RuntimeGraph.from_component(_tree(8))
    second = RuntimeGraph.from_component(_tree(8))
    first_cache = ResolutionCache(max_entries=16)
    second_cache = ResolutionCache(max_entries=16)
    for node in first.nodes.values():
        resolve_component(first, node.id, cache=first_cache)
    for node in second.nodes.values():
        resolve_component(second, node.id, cache=second_cache)
    assert first_cache.stats.misses == 8
    assert second_cache.stats.misses == 8
    assert second_cache.stats.hits == 0


def test_graph_rebuild_without_topology_change_reuses_identity_over_frame_boundaries():
    root = _tree(16)
    graph = RuntimeGraph.from_component(root)
    cache = ResolutionCache(max_entries=32)
    first = resolve_component(graph, "node-00001", cache=cache)
    graph = graph.rebuild()
    second = resolve_component(graph, "node-00001", cache=cache)
    assert first is second
    assert cache.stats.misses == 1
    assert cache.stats.hits == 1
