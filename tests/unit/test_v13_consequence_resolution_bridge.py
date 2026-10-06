from __future__ import annotations

from visual_engine.runtime.consequence_aggregation import aggregate_consequence_requests
from visual_engine.runtime.consequence_bindings import (
    ConsequenceBindingSet, EffectConsequenceBinding, StateConsequenceBinding,
    apply_consequence_binding_result, compile_resolved_consequences,
)
from visual_engine.runtime.consequences import ConsequenceKind, ConsequenceRequest
from visual_engine.runtime.contract import ResolutionContext, resolve_component
from visual_engine.runtime.effects import VisualEffect
from visual_engine.runtime.graph import RuntimeGraph
from visual_engine.model import Component, GeometryContract
from visual_engine.model.visual_contract import VisualContract
from visual_engine.runtime.versioning import context_fingerprint


def _graph():
    c = Component(id="target", kind="test", geometry=GeometryContract(), visual=VisualContract(fill_color="#ffffff"))
    return RuntimeGraph.from_component(c)


def _request(kind, consequence, precedence=5):
    return ConsequenceRequest(
        "rule", kind, "target", "region",
        ("target", "region", "source", "visibility"),
        {"consequence": consequence}, precedence,
    )


def test_binding_result_enters_existing_resolution_policies():
    aggregated = aggregate_consequence_requests([_request(ConsequenceKind.STATE, "covered", 20), _request(ConsequenceKind.EFFECT, "occlude", 7)])
    bindings = ConsequenceBindingSet(
        states=(StateConsequenceBinding("covered", "covered", group="coverage"),),
        effects=(EffectConsequenceBinding("occlude", "occlusion", alpha=.4),),
    )
    bound = compile_resolved_consequences(aggregated, bindings)
    context = apply_consequence_binding_result(ResolutionContext(), bound)
    result = resolve_component(_graph(), "target", context=context)
    assert result.visual.active_states == ("covered",)
    assert result.visual.visibility < 1.0
    assert len(result.visual.applied_effect_ids) == 1


def test_bridge_does_not_create_a_second_state_precedence_engine():
    aggregated = aggregate_consequence_requests([
        _request(ConsequenceKind.STATE, "open", 10),
        ConsequenceRequest("b", ConsequenceKind.STATE, "target", "region", ("target", "region", "b", "visibility"), {"consequence": "closed"}, 20),
    ])
    bindings = ConsequenceBindingSet(states=(
        StateConsequenceBinding("open", "open", group="lid"),
        StateConsequenceBinding("closed", "closed", group="lid"),
    ))
    bound = compile_resolved_consequences(aggregated, bindings)
    result = resolve_component(_graph(), "target", context=apply_consequence_binding_result(ResolutionContext(), bound))
    assert result.visual.active_states == ("closed",)


def test_target_scoped_consequence_changes_invalidate_resolution_context_only_for_target():
    base = ResolutionContext()
    a = apply_consequence_binding_result(base, compile_resolved_consequences(
        aggregate_consequence_requests([_request(ConsequenceKind.EFFECT, "occlude")]),
        ConsequenceBindingSet(effects=(EffectConsequenceBinding("occlude", "occlusion", alpha=.2),)),
    ))
    assert context_fingerprint(base, "other") != context_fingerprint(a, "target")
    # The effect is explicitly targeted to target, so an unrelated component does not
    # inherit this consequence through context fingerprinting.
    assert context_fingerprint(base, "other") == context_fingerprint(a, "other")


def test_duplicate_effect_ids_fail_closed_at_context_boundary():
    effect = VisualEffect("same", "occlusion", alpha=.1)
    try:
        apply_consequence_binding_result(ResolutionContext(effects=(effect,)), type("R", (), {"target_id": "target", "states": (), "effects": (effect,)})())
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate effect IDs must fail closed")


def test_geometry_and_appearance_remain_unbound():
    aggregated = aggregate_consequence_requests([_request(ConsequenceKind.GEOMETRY, "deform"), _request(ConsequenceKind.APPEARANCE, "red")])
    bound = compile_resolved_consequences(aggregated, ConsequenceBindingSet())
    context = apply_consequence_binding_result(ResolutionContext(), bound)
    assert not context.consequence_states and not context.effects
    assert len(bound.unbound) == 2
