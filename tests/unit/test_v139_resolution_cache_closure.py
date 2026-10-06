from __future__ import annotations

from dataclasses import replace

import pytest

from visual_engine.model import Component, GeometryContract, VisualContract
from visual_engine.runtime.consequence_aggregation import aggregate_consequence_requests
from visual_engine.runtime.consequence_bindings import (
    ConsequenceBindingSet,
    EffectConsequenceBinding,
    apply_consequence_binding_result,
    compile_resolved_consequences,
)
from visual_engine.runtime.consequences import ConsequenceKind, ConsequenceRequest
from visual_engine.runtime.contract import ResolutionContext, resolve_component
from visual_engine.runtime.dependencies import relation_effects
from visual_engine.runtime.effects import VisualEffect
from visual_engine.runtime.effect_color import apply_effect_color
from visual_engine.runtime.color_spaces import ColorRGBA
from visual_engine.runtime.graph import RuntimeGraph
from visual_engine.runtime.resolution_cache import ResolutionCache
from visual_engine.runtime.versioning import VersionStamp, context_fingerprint, resolution_fingerprint
from visual_engine.components.common.meta import Relation


def _graph() -> RuntimeGraph:
    root = Component("root", "root", visual=VisualContract(fill_color="#808080"))
    hand = Component("hand", "hand")
    face = Component("face", "face")
    root.add_child(hand)
    root.add_child(face)
    return RuntimeGraph.from_component(root)


def _graph_with_relation(metadata: dict) -> RuntimeGraph:
    root = Component("root", "root")
    hand = Component("hand", "hand")
    face = Component("face", "face")
    hand.relations.append(Relation("hand", "CUSTOM", "face", metadata=metadata))
    root.add_child(hand)
    root.add_child(face)
    return RuntimeGraph.from_component(root)


def _effect(effect_id="fx", *, priority=1, alpha=.5, color="#000000", source_id="source") -> VisualEffect:
    return VisualEffect(effect_id, "shadow", priority=priority, alpha=alpha, color=color, source_id=source_id)


def test_context_effects_are_canonicalized_but_semantic_order_is_fingerprinted():
    a = _effect("a", priority=1)
    b = _effect("b", priority=2, color="#ffffff", source_id="source-b")
    first = ResolutionContext(effects=(a, b))
    reversed_input = ResolutionContext(effects=(b, a))
    assert tuple(x.effect_id for x in first.effects) == ("a", "b")
    assert context_fingerprint(first, "root") == context_fingerprint(reversed_input, "root")

    changed_priority = ResolutionContext(effects=(replace(a, priority=3), b))
    assert context_fingerprint(first, "root") != context_fingerprint(changed_priority, "root")


@pytest.mark.parametrize(
    "mutation",
    [
        lambda e: replace(e, color="#010203"),
        lambda e: replace(e, alpha=.7),
        lambda e: replace(e, source_id="source-b"),
        lambda e: replace(e, effect_id="fx-b"),
        lambda e: replace(e, priority=2),
    ],
)
def test_direct_context_effect_mutations_invalidate_resolution_identity(mutation):
    graph = _graph()
    base = _effect()
    first = resolution_fingerprint(graph, "face", ResolutionContext(effects=(base,)))
    changed = resolution_fingerprint(graph, "face", ResolutionContext(effects=(mutation(base),)))
    assert first.cache_identity != changed.cache_identity



def test_inert_context_state_priority_does_not_false_invalidate_without_active_states():
    graph = _graph()
    a = ResolutionContext(state_priority=1000)
    b = ResolutionContext(state_priority=2000)
    assert resolution_fingerprint(graph, "face", a).cache_identity == resolution_fingerprint(graph, "face", b).cache_identity


def test_context_state_priority_does_invalidate_when_active_states_use_it():
    graph = _graph()
    a = ResolutionContext(active_states=("wet",), state_priority=1000)
    b = ResolutionContext(active_states=("wet",), state_priority=2000)
    assert resolution_fingerprint(graph, "face", a).cache_identity != resolution_fingerprint(graph, "face", b).cache_identity

def test_legacy_shadow_is_in_context_identity_and_cache_key():
    graph = _graph()
    a = resolution_fingerprint(graph, "face", ResolutionContext(shadow_alpha=.2, shadow_color="#000000"))
    b = resolution_fingerprint(graph, "face", ResolutionContext(shadow_alpha=.3, shadow_color="#000000"))
    c = resolution_fingerprint(graph, "face", ResolutionContext(shadow_alpha=.2, shadow_color="#ffffff"))
    assert a.cache_identity != b.cache_identity
    assert a.cache_identity != c.cache_identity


def test_relation_effect_changes_invalidate_target_resolution():
    before_graph = _graph_with_relation({"effect": {"kind": "shadow", "alpha": .25, "color": "#000000"}})
    before = resolution_fingerprint(before_graph, "face", ResolutionContext())
    relation = before_graph.get("hand").component.relations[0]
    relation.metadata["effect"]["alpha"] = .75
    after_graph = RuntimeGraph.from_component(before_graph.get("root").component)
    after = resolution_fingerprint(after_graph, "face", ResolutionContext())
    assert before.cache_identity != after.cache_identity


def _consequence_context(alpha: float) -> ResolutionContext:
    request = ConsequenceRequest(
        "rule", ConsequenceKind.EFFECT, "face", "region",
        ("face", "region", "source", "visibility"),
        {"consequence": "shade"}, 7,
    )
    aggregated = aggregate_consequence_requests([request])
    bindings = ConsequenceBindingSet(effects=(EffectConsequenceBinding("shade", "shadow", alpha=alpha, color="#101010"),))
    return apply_consequence_binding_result(
        ResolutionContext(), compile_resolved_consequences(aggregated, bindings)
    )


def test_consequence_effect_is_in_context_identity_and_invalidates():
    graph = _graph()
    a = resolution_fingerprint(graph, "face", _consequence_context(.2))
    b = resolution_fingerprint(graph, "face", _consequence_context(.4))
    assert a.cache_identity != b.cache_identity


def test_local_effect_color_fingerprint_and_global_resolution_fingerprint_change_together():
    graph = _graph()
    base = ColorRGBA.from_hex("#304050")
    local_a = apply_effect_color(base, ColorRGBA.from_hex("#a0b0c0"), effect_alpha=.4, lineage=("source", "fx"))
    local_b = apply_effect_color(base, ColorRGBA.from_hex("#a0b0c1"), effect_alpha=.4, lineage=("source", "fx"))
    global_a = resolution_fingerprint(graph, "face", ResolutionContext(effects=(_effect(color="#a0b0c0"),)))
    global_b = resolution_fingerprint(graph, "face", ResolutionContext(effects=(_effect(color="#a0b0c1"),)))
    assert local_a.fingerprint != local_b.fingerprint
    assert global_a.cache_identity != global_b.cache_identity
    assert local_a.fingerprint != global_a.cache_identity


def test_duplicate_effect_ids_fail_on_direct_and_mixed_paths():
    duplicate = _effect("same")
    with pytest.raises(ValueError, match="effect IDs must be unique"):
        ResolutionContext(effects=(duplicate, duplicate))

    graph = _graph_with_relation({
        "effect": {"effect_id": "same", "kind": "shadow", "alpha": .5, "color": "#000000"}
    })
    with pytest.raises(ValueError, match="effect IDs must be unique"):
        resolve_component(graph, "face", context=ResolutionContext(effects=(_effect("same"),)))


def test_resolution_fingerprint_changes_with_explicit_version():
    graph = _graph()
    context = ResolutionContext(effects=(_effect(),))
    older = resolution_fingerprint(graph, "face", context, VersionStamp(resolution="19"))
    current = resolution_fingerprint(graph, "face", context, VersionStamp(resolution="20"))
    assert older.cache_identity != current.cache_identity


def test_resolution_cache_real_hit_and_invalidation_for_color_alpha_order_source_id_and_version():
    graph = _graph()
    cache = ResolutionCache(max_entries=16)
    base = _effect("a", priority=1, alpha=.25, color="#000000", source_id="s")
    ctx = ResolutionContext(effects=(base,))

    first = resolve_component(graph, "face", context=ctx, cache=cache)
    second = resolve_component(graph, "face", context=ctx, cache=cache)
    assert first is second
    assert cache.stats.misses == 1
    assert cache.stats.hits == 1

    mutations = (
        replace(base, color="#010203"),
        replace(base, alpha=.5),
        replace(base, source_id="s2"),
        replace(base, effect_id="b"),
        replace(base, priority=2),
    )
    for changed in mutations:
        resolve_component(graph, "face", context=ResolutionContext(effects=(changed,)), cache=cache)
    assert cache.stats.misses == 1 + len(mutations)

    # Input order is canonicalized and therefore remains a hit.
    b = replace(base, effect_id="b", priority=2, color="#ffffff")
    canonical_a = ResolutionContext(effects=(base, b))
    canonical_b = ResolutionContext(effects=(b, base))
    resolve_component(graph, "face", context=canonical_a, cache=cache)
    misses_before = cache.stats.misses
    resolve_component(graph, "face", context=canonical_b, cache=cache)
    assert cache.stats.misses == misses_before
    assert cache.stats.hits >= 2



def test_all_effect_generation_paths_enter_the_same_cache_identity_contract():
    direct_graph = _graph()
    direct_context = ResolutionContext(effects=(_effect("direct", alpha=.2),))
    legacy_context = ResolutionContext(shadow_alpha=.2, shadow_color="#101010")
    relation_graph = _graph_with_relation({"effect": {"kind": "shadow", "alpha": .2, "color": "#101010"}})
    consequence = _consequence_context(.2)

    for graph, context in ((direct_graph, direct_context), (direct_graph, legacy_context), (relation_graph, ResolutionContext()), (direct_graph, consequence)):
        cache = ResolutionCache(max_entries=4)
        first = resolve_component(graph, "face", context=context, cache=cache)
        second = resolve_component(graph, "face", context=context, cache=cache)
        assert first is second
        assert cache.stats.misses == 1
        assert cache.stats.hits == 1


def test_relation_and_consequence_mutations_force_real_cache_misses():
    relation_graph = _graph_with_relation({"effect": {"kind": "shadow", "alpha": .2, "color": "#101010"}})
    cache = ResolutionCache(max_entries=8)
    resolve_component(relation_graph, "face", cache=cache)
    relation_graph.get("hand").component.relations[0].metadata["effect"]["alpha"] = .4
    rebuilt_relation_graph = RuntimeGraph.from_component(relation_graph.get("root").component)
    resolve_component(rebuilt_relation_graph, "face", cache=cache)
    assert cache.stats.misses == 2

    consequence_cache = ResolutionCache(max_entries=8)
    resolve_component(_graph(), "face", context=_consequence_context(.2), cache=consequence_cache)
    resolve_component(_graph(), "face", context=_consequence_context(.4), cache=consequence_cache)
    assert consequence_cache.stats.misses == 2


def test_cache_version_change_forces_miss():
    graph = _graph()
    cache = ResolutionCache(max_entries=8)
    context = ResolutionContext(effects=(_effect(),))
    resolve_component(graph, "face", context=context, version=VersionStamp(resolution="19"), cache=cache)
    resolve_component(graph, "face", context=context, version=VersionStamp(resolution="20"), cache=cache)
    assert cache.stats.misses == 2

def test_resolution_cache_does_not_change_color_or_provenance():
    graph = _graph()
    context = ResolutionContext(effects=(_effect("fx", alpha=.4, color="#112233"),))
    uncached = resolve_component(graph, "face", context=context)
    cache = ResolutionCache()
    cached_miss = resolve_component(graph, "face", context=context, cache=cache)
    cached_hit = resolve_component(graph, "face", context=context, cache=cache)
    assert cached_miss.visual.effective_fill_color == uncached.visual.effective_fill_color
    assert cached_miss.visual.effective_contour.color == uncached.visual.effective_contour.color
    assert cached_miss.provenance == uncached.provenance
    assert cached_hit.provenance == uncached.provenance
    assert cached_hit.visual == uncached.visual


def test_cache_eviction_is_bounded_and_deterministic():
    graph = _graph()
    cache = ResolutionCache(max_entries=2)
    for idx in range(3):
        resolve_component(
            graph, "face",
            context=ResolutionContext(effects=(_effect(str(idx), priority=idx, alpha=.2),)),
            cache=cache,
        )
    assert len(cache) == 2
    assert cache.stats.evictions == 1
