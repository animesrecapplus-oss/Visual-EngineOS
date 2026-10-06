from visual_engine.model import Component, Relation, VisualContract, Parameter
from visual_engine.runtime import (
    RuntimeGraph,
    ResolutionContext,
    build_relation_dependency_index,
    invalidation_reasons,
    relation_direction,
    relation_effects,
    resolve_component,
)
from visual_engine.runtime.versioning import dependency_fingerprint


def _graph_with_relation(relation: Relation):
    root = Component("root", "root", visual=VisualContract(fill_color="#ffffff"))
    hand = Component("hand", "hand")
    face = Component("face", "face")
    unrelated = Component("unrelated", "other")
    root.add_child(hand)
    root.add_child(face)
    root.add_child(unrelated)
    hand.relations.append(relation)
    return RuntimeGraph.from_component(root)


def test_known_relation_directions_are_explicit():
    assert relation_direction(Relation("a", "OCCLUSION", "b")) == "source_to_target"
    assert relation_direction(Relation("a", "CONTACT", "b")) == "bidirectional"
    assert relation_direction(Relation("a", "future_relation", "b")) == "none"
    assert relation_direction(Relation("a", "future_relation", "b", {"dependency_direction": "target_to_source"})) == "target_to_source"


def test_relation_dependency_index_crosses_sibling_branches():
    graph = _graph_with_relation(Relation("hand", "OCCLUSION", "face"))
    index = build_relation_dependency_index(graph)
    edges = index.dependencies_of("face")
    assert [(e.dependent_id, e.dependency_id, e.relation_type) for e in edges] == [("face", "hand", "OCCLUSION")]
    assert index.dependency_closure("face") == ("hand",)
    assert index.dependency_closure("hand") == ()


def test_relation_invalidation_is_target_scoped():
    graph = _graph_with_relation(Relation("hand", "OCCLUSION", "face"))
    reasons = invalidation_reasons(graph, "face", "hand")
    assert len(reasons) == 1
    assert "semantic relation dependency" in reasons[0].reason
    assert not invalidation_reasons(graph, "unrelated", "hand")


def test_bidirectional_relation_invalidates_both_sides():
    graph = _graph_with_relation(Relation("hand", "CONTACT", "face"))
    assert invalidation_reasons(graph, "face", "hand")
    assert invalidation_reasons(graph, "hand", "face")


def test_relation_dependencies_are_transitive():
    root = Component("root", "root")
    a = Component("a", "a")
    b = Component("b", "b")
    c = Component("c", "c")
    root.add_child(a); root.add_child(b); root.add_child(c)
    a.relations.append(Relation("a", "DEFORMATION", "b"))
    b.relations.append(Relation("b", "EXPRESSIVE", "c"))
    graph = RuntimeGraph.from_component(root)
    index = build_relation_dependency_index(graph)
    assert index.dependency_closure("c") == ("a", "b")
    assert invalidation_reasons(graph, "c", "a")


def test_relation_dependency_changes_fingerprint_for_cross_branch_source():
    relation = Relation("hand", "OCCLUSION", "face")
    graph = _graph_with_relation(relation)
    before = dependency_fingerprint(graph, "face")
    graph.get("hand").component.parameters["pressure"] = Parameter("pressure", 0.5)
    changed = RuntimeGraph.from_component(graph.get("root").component)
    assert dependency_fingerprint(changed, "face") != before


def test_relation_metadata_effect_compiles_to_normal_visual_effect():
    relation = Relation(
        "hand", "OCCLUSION", "face",
        metadata={"effect": {"kind": "occlusion", "alpha": 0.75, "opacity_factor": 0.9}},
    )
    graph = _graph_with_relation(relation)
    effects = relation_effects(graph, "face")
    assert len(effects) == 1
    assert effects[0].kind == "occlusion"
    assert effects[0].alpha == 0.75
    assert effects[0].source_id == "hand"
    assert effects[0].target_id == "face"


def test_relation_effect_participates_in_component_resolution():
    relation = Relation("hand", "OCCLUSION", "face", metadata={"effect": {"kind": "occlusion", "alpha": 1.0}})
    graph = _graph_with_relation(relation)
    result = resolve_component(graph, "face")
    assert result.visual.visibility == 0.0
    assert result.visual.applied_effect_ids


def test_relation_effect_can_target_source_or_be_global():
    source_target = Relation("hand", "OCCLUSION", "face", metadata={
        "effect": {"kind": "visibility", "visibility_factor": 0.5},
        "effect_target": "source",
    })
    graph = _graph_with_relation(source_target)
    assert relation_effects(graph, "hand")[0].target_id == "hand"
    assert not relation_effects(graph, "face")

    global_relation = Relation("hand", "SEMANTIC", "face", metadata={
        "effect": {"kind": "visibility", "visibility_factor": 0.5},
        "effect_target": None,
    })
    graph2 = _graph_with_relation(global_relation)
    assert relation_effects(graph2, "hand")[0].target_id is None
    assert relation_effects(graph2, "face")[0].target_id is None


def test_effect_declaration_is_a_dependency_even_when_relation_direction_is_none():
    relation = Relation(
        "hand", "CUSTOM", "face",
        metadata={"effect": {"kind": "occlusion", "alpha": 0.5}, "dependency_direction": "none"},
    )
    graph = _graph_with_relation(relation)
    assert invalidation_reasons(graph, "face", "hand")


def test_global_relation_effect_invalidates_every_visual_target():
    relation = Relation(
        "hand", "CUSTOM", "face",
        metadata={"effect": {"kind": "tint", "alpha": 0.2, "color": "#ff0000"}, "effect_target": None},
    )
    graph = _graph_with_relation(relation)
    assert invalidation_reasons(graph, "face", "hand")
    assert invalidation_reasons(graph, "unrelated", "hand")


def test_relation_dependency_includes_source_ancestors():
    root = Component("root", "root")
    hand = Component("hand", "hand")
    hand_parent = Component("hand_parent", "arm")
    face = Component("face", "face")
    root.add_child(hand_parent)
    hand_parent.add_child(hand)
    root.add_child(face)
    hand.relations.append(Relation("hand", "OCCLUSION", "face"))
    graph = RuntimeGraph.from_component(root)
    index = build_relation_dependency_index(graph)
    assert index.relation_dependency_nodes(graph, "face") == ("hand", "hand_parent", "root")
    assert invalidation_reasons(graph, "face", "hand_parent")


def test_relation_dependency_cycle_is_finite_and_deterministic():
    root = Component("root", "root")
    a = Component("a", "a")
    b = Component("b", "b")
    c = Component("c", "c")
    root.add_child(a); root.add_child(b); root.add_child(c)
    a.relations.append(Relation("a", "CONTACT", "b"))
    b.relations.append(Relation("b", "CONTACT", "a"))
    b.relations.append(Relation("b", "OCCLUSION", "c"))
    graph = RuntimeGraph.from_component(root)
    index = build_relation_dependency_index(graph)
    assert index.dependency_closure("c") == ("a", "b")
    assert index.dependency_closure("a") == ("b",)


def test_relation_effect_metadata_change_invalidates_target():
    relation = Relation("hand", "CUSTOM", "face", metadata={"effect": {"kind": "occlusion", "alpha": 0.25}})
    graph = _graph_with_relation(relation)
    before = dependency_fingerprint(graph, "face")
    relation.metadata["effect"]["alpha"] = 0.75
    changed = RuntimeGraph.from_component(graph.get("root").component)
    assert dependency_fingerprint(changed, "face") != before


def test_relation_effect_provenance_preserves_relation_source():
    relation = Relation("hand", "OCCLUSION", "face", metadata={"effect": {"kind": "occlusion", "alpha": 0.5}})
    graph = _graph_with_relation(relation)
    result = resolve_component(graph, "face")
    assert result.provenance.for_field("effects")[-1].component_id == "face"
    assert any(step.component_id == "hand" and step.field == "occlusion" and step.action == "apply" for step in result.provenance.steps)
