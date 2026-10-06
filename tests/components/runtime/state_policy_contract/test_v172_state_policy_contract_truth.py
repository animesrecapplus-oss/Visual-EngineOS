from __future__ import annotations

from visual_engine.runtime import StateActivation, StateDecision
from visual_engine.runtime.state_policy import StateActivation as CompatActivation
from visual_engine.runtime.state_policy import StateDecision as CompatDecision
from visual_engine.runtime.state_policy_contract import StateActivation as CanonicalActivation
from visual_engine.runtime.state_policy_contract import StateDecision as CanonicalDecision


def test_canonical_contract_owns_public_and_compatibility_identity() -> None:
    assert StateActivation is CanonicalActivation
    assert StateDecision is CanonicalDecision
    assert CompatActivation is CanonicalActivation
    assert CompatDecision is CanonicalDecision


def test_activation_contract_preserves_precedence_semantics() -> None:
    activation = StateActivation("wet", "source-a", 2, 3, "appearance", ("dry",), ("open",), 1)
    assert activation.precedence_key == (2, 1, 3, "wet", "source-a")


def test_contracts_are_immutable_and_decision_references_activation() -> None:
    activation = StateActivation("wet", "source-a", 2, 3, None, (), (), 1)
    decision = StateDecision(activation, "accept", "passed group/conflict precedence")
    assert decision.candidate is activation
    try:
        activation.name = "changed"
    except AttributeError:
        pass
    else:
        raise AssertionError("StateActivation must remain frozen")


def test_contract_module_has_no_policy_algorithm_owner() -> None:
    import visual_engine.runtime.state_policy_contract as contract

    names = set(vars(contract))
    assert "collect_state_activations" not in names
    assert "resolve_state_activations_with_decisions" not in names
    assert "resolve_states_with_decisions" not in names
