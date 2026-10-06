from __future__ import annotations

import pytest

from visual_engine.runtime.consequence_aggregation import (
    ConsequenceAggregationResult, ConsequencePolicy, ResolvedConsequence,
    ConsequenceProvenance, aggregate_consequence_requests, AggregationMode,
)
from visual_engine.runtime.consequence_bindings import (
    ConsequenceBindingSet, EffectConsequenceBinding, StateConsequenceBinding,
    compile_resolved_consequences,
)
from visual_engine.runtime.consequences import ConsequenceKind, ConsequenceRequest
from visual_engine.runtime.effects import VisualEffect
from visual_engine.runtime.state_policy import resolve_state_activations


def req(kind, consequence, precedence=5):
    return ConsequenceRequest("rule", kind, "target", "eye", ("target", "eye", "occ", "visibility"), {"consequence": consequence}, precedence)


def test_state_consequence_compiles_to_existing_state_activation_contract():
    r = aggregate_consequence_requests([req(ConsequenceKind.STATE, "covered")])
    bindings = ConsequenceBindingSet(states=(StateConsequenceBinding("covered", "covered", group="lid"),))
    out = compile_resolved_consequences(r, bindings)
    assert [x.name for x in out.states] == ["covered"]
    assert not out.effects
    assert not out.unbound
    assert resolve_state_activations(out.states)[0].name == "covered"


def test_state_precedence_is_not_reimplemented_by_binding_compiler():
    requests = [req(ConsequenceKind.STATE, "open", 10), req(ConsequenceKind.STATE, "closed", 20)]
    # Different rule IDs/source keys are needed so the requests remain distinct.
    requests[0] = ConsequenceRequest("a", ConsequenceKind.STATE, "target", "eye", ("target", "eye", "a", "visibility"), {"consequence": "open"}, 10)
    requests[1] = ConsequenceRequest("b", ConsequenceKind.STATE, "target", "eye", ("target", "eye", "b", "visibility"), {"consequence": "closed"}, 20)
    r = aggregate_consequence_requests(requests, [ConsequencePolicy("lid", AggregationMode.KEEP_ALL)])
    bindings = ConsequenceBindingSet(states=(
        StateConsequenceBinding("open", "open", group="lid"),
        StateConsequenceBinding("closed", "closed", group="lid"),
    ))
    out = compile_resolved_consequences(r, bindings)
    accepted = resolve_state_activations(out.states)
    assert [x.name for x in accepted] == ["closed"]


def test_effect_consequence_compiles_to_existing_visual_effect_contract():
    r = aggregate_consequence_requests([req(ConsequenceKind.EFFECT, "occlude", 7)])
    bindings = ConsequenceBindingSet(effects=(EffectConsequenceBinding(
        "occlude", "occlusion", alpha=0.4, visibility_factor=0.8,
    ),))
    out = compile_resolved_consequences(r, bindings)
    assert len(out.effects) == 1
    effect = out.effects[0]
    assert isinstance(effect, VisualEffect)
    assert effect.kind == "occlusion"
    assert effect.alpha == 0.4
    assert effect.visibility_factor == 0.8


def test_missing_binding_fails_loss_aware_instead_of_guessing():
    r = aggregate_consequence_requests([req(ConsequenceKind.STATE, "unknown")])
    out = compile_resolved_consequences(r, ConsequenceBindingSet())
    assert not out.states
    assert not out.effects
    assert len(out.unbound) == 1


def test_geometry_and_appearance_are_not_guessed_into_state_or_effect():
    r = aggregate_consequence_requests([
        req(ConsequenceKind.GEOMETRY, "deform"),
        req(ConsequenceKind.APPEARANCE, "red"),
    ])
    bindings = ConsequenceBindingSet(
        states=(StateConsequenceBinding("deform", "bad_guess"),),
        effects=(EffectConsequenceBinding("red", "tint"),),
    )
    out = compile_resolved_consequences(r, bindings)
    assert len(out.unbound) == 2
    assert not out.states and not out.effects
