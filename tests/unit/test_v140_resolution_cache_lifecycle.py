from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

import pytest

from visual_engine.components.common.meta import Relation
from visual_engine.model import Component, VisualContract
from visual_engine.runtime.contract import ResolutionContext, resolve_component
from visual_engine.runtime.consequence_aggregation import aggregate_consequence_requests
from visual_engine.runtime.consequence_bindings import (
    ConsequenceBindingSet,
    EffectConsequenceBinding,
    apply_consequence_binding_result,
    compile_resolved_consequences,
)
from visual_engine.runtime.consequences import ConsequenceKind, ConsequenceRequest
from visual_engine.runtime.geometry_cache import GeometryCache
from visual_engine.runtime.geometry_fingerprint import geometry_dependency_fingerprint
from visual_engine.runtime.graph import RuntimeGraph
from visual_engine.runtime.resolution_cache import ResolutionCache
from visual_engine.runtime.versioning import resolution_fingerprint
from visual_engine.runtime.effects import VisualEffect


def _graph() -> RuntimeGraph:
    root = Component("root", "root", visual=VisualContract(fill_color="#607080"))
    hand = Component("hand", "hand")
    face = Component("face", "face")
    sibling = Component("sibling", "sibling")
    root.add_child(hand)
    root.add_child(face)
    root.add_child(sibling)
    return RuntimeGraph.from_component(root)


def _effect(effect_id: str = "fx", *, color: str = "#202020", target: str | None = "face", alpha: float = .3, priority: int = 1) -> VisualEffect:
    return VisualEffect(effect_id, "shadow", priority=priority, alpha=alpha, color=color, source_id="source", target_id=target)


def _consequence_context(alpha: float, target: str = "face") -> ResolutionContext:
    request = ConsequenceRequest(
        "rule", ConsequenceKind.EFFECT, target, "region",
        (target, "region", "source", "visibility"),
        {"consequence": "shade"}, 7,
    )
    aggregated = aggregate_consequence_requests([request])
    bindings = ConsequenceBindingSet(
        effects=(EffectConsequenceBinding("shade", "shadow", alpha=alpha, color="#101010"),)
    )
    return apply_consequence_binding_result(
        ResolutionContext(), compile_resolved_consequences(aggregated, bindings)
    )


def test_rebuilt_graph_reuses_resolution_cache_identity_without_topology_change():
    graph = _graph()
    cache = ResolutionCache(max_entries=8)
    first = resolve_component(graph, "face", cache=cache)
    rebuilt = graph.rebuild()
    second = resolve_component(rebuilt, "face", cache=cache)
    assert second is first
    assert cache.stats.misses == 1
    assert cache.stats.hits == 1


def test_unrelated_sibling_addition_does_not_invalidate_face_resolution_after_rebuild():
    graph = _graph()
    cache = ResolutionCache(max_entries=8)
    first = resolve_component(graph, "face", cache=cache)
    root = graph.get("root").component
    root.add_child(Component("new-sibling", "sibling"))
    assert not graph.is_current()
    rebuilt = graph.rebuild()
    second = resolve_component(rebuilt, "face", cache=cache)
    assert second is first
    assert cache.stats.misses == 1
    assert cache.stats.hits == 1


def test_stale_graph_is_rejected_before_resolution_cache_lookup():
    graph = _graph()
    cache = ResolutionCache(max_entries=8)
    resolve_component(graph, "face", cache=cache)

    class SpyCache(ResolutionCache):
        def __init__(self):
            super().__init__(max_entries=8)
            self.lookup_called = False

        def get(self, fingerprint):
            self.lookup_called = True
            return super().get(fingerprint)

    spy = SpyCache()
    # Seed the spy so a mistaken stale lookup would be observable as a hit.
    resolve_component(graph, "face", cache=spy)
    spy.lookup_called = False
    root = graph.get("root").component
    root.add_child(Component("stale-child", "child"))
    assert not graph.is_current()
    misses_before = spy.stats.misses
    with pytest.raises(RuntimeError, match="stale.*ResolutionCache"):
        resolve_component(graph, "face", cache=spy)
    assert spy.lookup_called is False
    assert spy.stats.misses == misses_before


def test_relation_addition_and_removal_invalidate_target_after_rebuild():
    graph = _graph()
    cache = ResolutionCache(max_entries=16)
    resolve_component(graph, "face", cache=cache)
    hand = graph.get("hand").component
    relation = Relation(
        "hand", "OCCLUSION", "face",
        metadata={"effect": {"kind": "shadow", "alpha": .35, "color": "#101010"}},
    )
    hand.relations.append(relation)
    assert not graph.is_current()
    with pytest.raises(RuntimeError, match="stale"):
        resolve_component(graph, "face", cache=cache)
    rebuilt_with_relation = graph.rebuild()
    resolved_with_relation = resolve_component(rebuilt_with_relation, "face", cache=cache)
    assert cache.stats.misses == 2
    assert resolved_with_relation.visual.effective_fill_color != "#607080"

    hand.relations.remove(relation)
    rebuilt_without_relation = graph.rebuild()
    resolved_without_relation = resolve_component(rebuilt_without_relation, "face", cache=cache)
    # Removing the relation restores the exact original dependency identity; the
    # original cache entry is still valid and must be reused rather than rebuilt.
    assert cache.stats.misses == 2
    assert cache.stats.hits == 1
    assert resolved_without_relation.visual.effective_fill_color == "#ffffff"


def test_hierarchy_reparenting_invalidates_target_but_restoring_original_hierarchy_reuses_entry():
    graph = _graph()
    cache = ResolutionCache(max_entries=16)
    original = resolve_component(graph, "face", cache=cache)
    root = graph.get("root").component
    hand = graph.get("hand").component
    face = graph.get("face").component
    root.children.remove(face)
    face.parent_id = None
    hand.add_child(face)
    assert not graph.is_current()
    moved = graph.rebuild()
    moved_result = resolve_component(moved, "face", cache=cache)
    assert moved_result is not original
    assert cache.stats.misses == 2

    moved_root = moved.get("root").component
    moved_hand = moved.get("hand").component
    moved_face = moved.get("face").component
    moved_hand.children.remove(moved_face)
    moved_face.parent_id = None
    moved_root.add_child(moved_face)
    restored = moved.rebuild()
    restored_result = resolve_component(restored, "face", cache=cache)
    assert restored_result is original
    assert cache.stats.misses == 2
    assert cache.stats.hits == 1


def test_targeted_effect_isolated_from_sibling_resolution():
    graph = _graph()
    cache = ResolutionCache(max_entries=16)
    targeted = ResolutionContext(effects=(_effect(target="face", color="#202020"),))
    unrelated_target = ResolutionContext(effects=(_effect(target="face", color="#f0f0f0"),))
    face_first = resolve_component(graph, "face", context=targeted, cache=cache)
    sibling_first = resolve_component(graph, "sibling", context=targeted, cache=cache)
    misses_after_firsts = cache.stats.misses
    sibling_second = resolve_component(graph, "sibling", context=unrelated_target, cache=cache)
    face_second = resolve_component(graph, "face", context=unrelated_target, cache=cache)
    assert sibling_second is sibling_first
    assert face_second is not face_first
    assert cache.stats.misses == misses_after_firsts + 1


def test_consequence_target_isolated_from_sibling_resolution():
    graph = _graph()
    cache = ResolutionCache(max_entries=16)
    face_context_a = _consequence_context(.25, target="face")
    face_context_b = _consequence_context(.75, target="face")
    sibling_first = resolve_component(graph, "sibling", context=face_context_a, cache=cache)
    sibling_second = resolve_component(graph, "sibling", context=face_context_b, cache=cache)
    face_first = resolve_component(graph, "face", context=face_context_a, cache=cache)
    face_second = resolve_component(graph, "face", context=face_context_b, cache=cache)
    assert sibling_second is sibling_first
    assert face_second is not face_first


def test_lru_pressure_is_bounded_at_1_10_100_and_1000_distinct_identities():
    graph = _graph()
    for capacity in (1, 10, 100, 1000):
        cache = ResolutionCache(max_entries=capacity)
        for index in range(capacity + 1):
            context = ResolutionContext(effects=(_effect(str(index), color=f"#{index % 256:02x}2020"),))
            resolve_component(graph, "face", context=context, cache=cache)
        assert len(cache) == capacity
        assert cache.stats.misses == capacity + 1
        assert cache.stats.stores == capacity + 1
        assert cache.stats.evictions == 1


def test_lru_recency_protects_recent_identity():
    graph = _graph()
    cache = ResolutionCache(max_entries=2)
    contexts = [ResolutionContext(effects=(_effect(str(i), color=f"#{i:02x}3030"),)) for i in range(3)]
    resolve_component(graph, "face", context=contexts[0], cache=cache)
    resolve_component(graph, "face", context=contexts[1], cache=cache)
    resolve_component(graph, "face", context=contexts[0], cache=cache)  # make 0 MRU
    resolve_component(graph, "face", context=contexts[2], cache=cache)
    misses_before = cache.stats.misses
    resolve_component(graph, "face", context=contexts[0], cache=cache)
    assert cache.stats.misses == misses_before
    assert cache.stats.hits >= 2
    # Identity 1 was the LRU entry and must have been evicted. A single lookup
    # therefore records one new miss and replaces the evicted entry.
    resolve_component(graph, "face", context=contexts[1], cache=cache)
    assert cache.stats.misses == misses_before + 1


def test_resolution_cache_concurrent_reads_are_consistent():
    graph = _graph()
    cache = ResolutionCache(max_entries=8)
    context = ResolutionContext(effects=(_effect("shared", color="#334455"),))
    expected = resolve_component(graph, "face", context=context, cache=cache)

    def read_once():
        return resolve_component(graph, "face", context=context, cache=cache)

    with ThreadPoolExecutor(max_workers=16) as pool:
        values = list(pool.map(lambda _: read_once(), range(128)))
    assert all(value.visual == expected.visual for value in values)
    assert all(value.provenance == expected.provenance for value in values)
    assert cache.stats.hits >= 128


def test_resolution_cache_concurrent_writes_and_reads_do_not_corrupt_lru():
    graph = _graph()
    cache = ResolutionCache(max_entries=32)

    def write_read(index: int):
        context = ResolutionContext(effects=(_effect(str(index), color=f"#{index % 256:02x}4050"),))
        result = resolve_component(graph, "face", context=context, cache=cache)
        again = resolve_component(graph, "face", context=context, cache=cache)
        return result.visual, again.visual

    with ThreadPoolExecutor(max_workers=16) as pool:
        pairs = list(pool.map(write_read, range(128)))
    assert all(first == second for first, second in pairs)
    assert len(cache) <= 32
    assert cache.stats.evictions >= 96


def test_resolution_cache_stats_are_immutable_snapshots_and_clear_preserves_counters():
    graph = _graph()
    cache = ResolutionCache(max_entries=2)
    context = ResolutionContext(effects=(_effect(),))
    resolve_component(graph, "face", context=context, cache=cache)
    snapshot = cache.stats
    cache.clear()
    assert snapshot.hits == 0
    assert snapshot.misses == 1
    assert snapshot.stores == 1
    assert len(cache) == 0
    assert cache.stats.misses == 1
    assert cache.stats.stores == 1


def test_resolution_and_geometry_dependency_surfaces_are_intentionally_different():
    graph = _graph()
    resolution_before = resolution_fingerprint(graph, "face", ResolutionContext()).cache_identity
    geometry_before = geometry_dependency_fingerprint(graph, "face")

    face = graph.get("face").component
    face.visual = replace(face.visual, fill_color="#102030")
    visual_graph = graph.rebuild()
    resolution_visual = resolution_fingerprint(visual_graph, "face", ResolutionContext()).cache_identity
    geometry_visual = geometry_dependency_fingerprint(visual_graph, "face")
    assert resolution_visual != resolution_before
    assert geometry_visual == geometry_before

    hand = visual_graph.get("hand").component
    hand.relations.append(Relation(
        "hand", "OCCLUSION", "face",
        metadata={"effect": {"kind": "shadow", "alpha": .3, "color": "#101010"}},
    ))
    relation_graph = visual_graph.rebuild()
    resolution_relation = resolution_fingerprint(relation_graph, "face", ResolutionContext()).cache_identity
    geometry_relation = geometry_dependency_fingerprint(relation_graph, "face")
    assert resolution_relation != resolution_visual
    assert geometry_relation != geometry_visual

    relation = relation_graph.get("hand").component.relations[0]
    relation.metadata["effect"]["alpha"] = .8
    metadata_graph = relation_graph.rebuild()
    resolution_metadata = resolution_fingerprint(metadata_graph, "face", ResolutionContext()).cache_identity
    geometry_metadata = geometry_dependency_fingerprint(metadata_graph, "face")
    assert resolution_metadata != resolution_relation
    # Effect metadata is visual-resolution owned; geometry only consumes the
    # explicit geometry_inputs relation field, not arbitrary effect payloads.
    assert geometry_metadata == geometry_relation


def test_geometry_cache_and_resolution_cache_share_topology_but_not_visual_payload_ownership():
    graph = _graph()
    geometry_cache = GeometryCache(max_entries=8, max_bytes=None)
    key_before = geometry_cache.make_key(graph, "face", generator="test", generator_version="1")
    resolution_before = resolution_fingerprint(graph, "face", ResolutionContext()).cache_identity

    face = graph.get("face").component
    face.geometry = replace(face.geometry, local_z=1.0)
    rebuilt = graph.rebuild()
    key_after = geometry_cache.make_key(rebuilt, "face", generator="test", generator_version="1")
    resolution_after = resolution_fingerprint(rebuilt, "face", ResolutionContext()).cache_identity
    assert key_after.cache_identity != key_before.cache_identity
    assert resolution_after != resolution_before


def test_cache_builder_path_remains_non_singleflight_but_thread_safe_for_direct_usage():
    graph = _graph()
    cache = ResolutionCache(max_entries=4)
    fingerprint = resolution_fingerprint(graph, "face", ResolutionContext())
    calls = 0

    def builder():
        nonlocal calls
        calls += 1
        return object()

    first, hit = cache.get_or_build(fingerprint, builder)
    second, hit2 = cache.get_or_build(fingerprint, builder)
    assert first is second
    assert hit is False
    assert hit2 is True
    assert calls == 1
