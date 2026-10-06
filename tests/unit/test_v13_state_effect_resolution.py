from visual_engine.model import Component, StateLayer, VisualContract
from visual_engine.runtime import RuntimeGraph, ResolutionContext, VisualEffect, resolve_component


def graph_with_child():
    root = Component("root", "root", visual=VisualContract(fill_color="#ffffff"))
    child = Component("child", "child")
    root.add_child(child)
    return RuntimeGraph.from_component(root)


def test_state_group_chooses_highest_precedence():
    root = Component("root", "root")
    root.add_state(StateLayer("open", priority=1, group="lid"))
    root.add_state(StateLayer("closed", priority=5, group="lid"))
    result = resolve_component(RuntimeGraph.from_component(root), "root")
    assert result.visual.active_states == ("closed",)


def test_target_specific_state_wins_equal_priority():
    root = Component("root", "root")
    root.add_state(StateLayer("ancestor", priority=4, group="mode"))
    child = Component("child", "child")
    child.add_state(StateLayer("target", priority=4, group="mode"))
    root.add_child(child)
    result = resolve_component(RuntimeGraph.from_component(root), "child")
    assert result.visual.active_states == ("target",)


def test_explicit_context_state_overrides_component_at_equal_priority():
    root = Component("root", "root")
    root.add_state(StateLayer("normal", priority=1000, group="mode"))
    graph = RuntimeGraph.from_component(root)
    result = resolve_component(graph, "root", context=ResolutionContext(active_states=("closed",), state_groups=(("closed", "mode"),)))
    assert result.visual.active_states == ("closed",)


def test_explicit_conflict_is_symmetric_and_deterministic():
    root = Component("root", "root")
    root.add_state(StateLayer("wet", priority=3, conflicts=("dry",)))
    root.add_state(StateLayer("dry", priority=2, conflicts=("wet",)))
    result = resolve_component(RuntimeGraph.from_component(root), "root")
    assert result.visual.active_states == ("wet",)


def test_state_requirements_are_fixed_point_resolved():
    root = Component("root", "root")
    root.add_state(StateLayer("irritated", requires=("open",)))
    result = resolve_component(RuntimeGraph.from_component(root), "root")
    assert result.visual.active_states == ()


def test_state_requirements_keep_valid_state():
    root = Component("root", "root")
    root.add_state(StateLayer("open", group="lid"))
    root.add_state(StateLayer("irritated", requires=("open",)))
    result = resolve_component(RuntimeGraph.from_component(root), "root")
    assert result.visual.active_states == ("irritated", "open")


def test_context_state_names_are_set_like_for_fingerprints():
    root = Component("root", "root")
    graph = RuntimeGraph.from_component(root)
    from visual_engine.runtime.versioning import resolution_fingerprint
    a = resolution_fingerprint(graph, "root", ResolutionContext(active_states=("wet", "cold")))
    b = resolution_fingerprint(graph, "root", ResolutionContext(active_states=("cold", "wet")))
    assert a.cache_identity == b.cache_identity


def test_effects_have_explicit_composition_laws():
    graph = graph_with_child()
    result = resolve_component(graph, "child", context=ResolutionContext(effects=(
        VisualEffect("shadow-low", "shadow", priority=1, alpha=.25, color="#000000"),
        VisualEffect("shadow-high", "shadow", priority=2, alpha=.5, color="#000000"),
        VisualEffect("fade", "opacity", priority=10, opacity_factor=.5),
        VisualEffect("hide", "visibility", priority=10, visibility_factor=.4),
    )))
    assert result.visual.shadow_alpha == .625
    assert result.visual.opacity == .5
    assert result.visual.visibility == .4
    assert result.visual.effective_fill_color == "#606060"


def test_effect_targeting_does_not_leak_to_sibling():
    root = Component("root", "root")
    a = Component("a", "child")
    b = Component("b", "child")
    root.add_child(a); root.add_child(b)
    graph = RuntimeGraph.from_component(root)
    effect = VisualEffect("shadow-a", "shadow", alpha=1.0, target_id="a")
    ra = resolve_component(graph, "a", context=ResolutionContext(effects=(effect,)))
    rb = resolve_component(graph, "b", context=ResolutionContext(effects=(effect,)))
    assert ra.visual.effective_fill_color == "#000000"
    assert rb.visual.effective_fill_color == "#ffffff"


def test_effect_order_is_canonical_not_insertion_order():
    graph = graph_with_child()
    a = VisualEffect("a", "shadow", priority=1, alpha=.5, color="#000000")
    b = VisualEffect("b", "shadow", priority=2, alpha=.5, color="#ff0000")
    ra = resolve_component(graph, "child", context=ResolutionContext(effects=(a,b)))
    rb = resolve_component(graph, "child", context=ResolutionContext(effects=(b,a)))
    assert ra.visual.effective_fill_color == rb.visual.effective_fill_color
    assert ra.fingerprint.cache_identity == rb.fingerprint.cache_identity


def test_provenance_records_rejected_and_applied_state_candidates():
    root = Component("root", "root")
    root.add_state(StateLayer("open", priority=1, group="lid"))
    root.add_state(StateLayer("closed", priority=2, group="lid"))
    result = resolve_component(RuntimeGraph.from_component(root), "root")
    details = [step.detail for step in result.provenance.for_field("states")]
    assert any("state=open" in d for d in details)
    assert any("state=closed" in d for d in details)
    assert any(step.action == "accept" for step in result.provenance.for_field("states"))


def test_same_state_name_is_resolved_once_from_nearest_precedence():
    root = Component("root", "root")
    root.add_state(StateLayer("wet", priority=1, values={"source": "root"}))
    child = Component("child", "child")
    child.add_state(StateLayer("wet", priority=1, values={"source": "child"}))
    root.add_child(child)
    result = resolve_component(RuntimeGraph.from_component(root), "child")
    assert result.visual.active_states == ("wet",)
    assert len([s for s in result.provenance.for_field("states") if s.action == "accept"]) == 1


def test_state_self_dependency_is_rejected():
    import pytest
    with pytest.raises(ValueError):
        StateLayer("wet", requires=("wet",))


def test_duplicate_effect_ids_are_rejected():
    import pytest
    a = VisualEffect("same", "shadow")
    with pytest.raises(ValueError):
        ResolutionContext(effects=(a, a))


def test_targeted_effect_context_fingerprint_is_scoped_to_target():
    from visual_engine.runtime.versioning import resolution_fingerprint
    graph = graph_with_child()
    root = graph.get("root").component
    a = Component("a", "child")
    b = Component("b", "child")
    # Build a separate graph with two siblings.
    root.children.clear(); root.add_child(a); root.add_child(b)
    graph = RuntimeGraph.from_component(root)
    effect = VisualEffect("only-a", "shadow", alpha=.5, target_id="a")
    context = ResolutionContext(effects=(effect,))
    fa = resolution_fingerprint(graph, "a", context)
    fb = resolution_fingerprint(graph, "b", context)
    empty_b = resolution_fingerprint(graph, "b", ResolutionContext())
    assert fb.cache_identity == empty_b.cache_identity
    assert fa.cache_identity != fb.cache_identity
