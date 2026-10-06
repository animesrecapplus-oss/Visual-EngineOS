from __future__ import annotations

import importlib
import math

import pytest

from visual_engine.runtime import ResolutionContext as PublicResolutionContext
from visual_engine.runtime.contract import ResolutionContext as CompatibilityResolutionContext
from visual_engine.runtime.effects import VisualEffect
from visual_engine.runtime.resolution_context import ResolutionContext
from visual_engine.runtime.state_policy import StateActivation


def _effect(effect_id: str = "fx", priority: int = 2) -> VisualEffect:
    return VisualEffect(effect_id, "shadow", priority=priority, alpha=0.25, color="#102030")


def test_canonical_owner_and_compatibility_identity() -> None:
    assert PublicResolutionContext is ResolutionContext
    assert CompatibilityResolutionContext is ResolutionContext
    assert "visual_engine.runtime.contract" not in ResolutionContext.__module__


def test_context_canonicalizes_order_and_preserves_effect_precedence() -> None:
    context = ResolutionContext(
        active_states=("wet", "covered", "wet"),
        state_groups=(("wet", "appearance"), ("covered", "state")),
        state_conflicts=(("wet", ("covered", "wet")),),
        state_requires=(("wet", ("base",)),),
        effects=(_effect("late", 4), _effect("early", 1)),
        consequence_states=(
            StateActivation("wet", "source-b", 2, 1, "g", (), (), 1),
            StateActivation("closed", "source-a", 1, 1, "g", (), (), 1),
        ),
    )
    assert context.active_states == ("covered", "wet")
    assert context.state_groups == (("covered", "state"), ("wet", "appearance"))
    assert context.state_conflicts == (("wet", ("covered", "wet")),)
    assert context.state_requires == (("wet", ("base",)),)
    assert tuple(e.effect_id for e in context.effects) == ("early", "late")
    assert tuple(s.name for s in context.consequence_states) == ("wet", "closed")


def test_context_rejects_non_finite_and_invalid_contract_values() -> None:
    for value in (math.nan, math.inf, -math.inf, -0.01, 1.01):
        with pytest.raises(ValueError, match="shadow_alpha"):
            ResolutionContext(shadow_alpha=value)
    with pytest.raises(ValueError, match="shadow_color"):
        ResolutionContext(shadow_color="#xyzxyz")
    with pytest.raises(ValueError, match="occluded_by"):
        ResolutionContext(occluded_by=("",))
    with pytest.raises(ValueError, match="state_priority"):
        ResolutionContext(state_priority="1000")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="effects"):
        ResolutionContext(effects=(object(),))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="consequence_states"):
        ResolutionContext(consequence_states=(object(),))  # type: ignore[arg-type]


def test_context_rejects_duplicate_effect_ids_and_duplicate_mapping_keys() -> None:
    effect = _effect()
    with pytest.raises(ValueError, match="effect IDs must be unique"):
        ResolutionContext(effects=(effect, effect))
    with pytest.raises(ValueError, match="state_groups keys"):
        ResolutionContext(state_groups=(("wet", "a"), ("wet", "b")))
    with pytest.raises(ValueError, match="state_conflicts keys"):
        ResolutionContext(state_conflicts=(("wet", ("a",)), ("wet", ("b",))))


def test_effective_effects_keeps_target_scope_and_legacy_shadow_boundary() -> None:
    context = ResolutionContext(
        shadow_alpha=0.25,
        shadow_color="#112233",
        effects=(
            VisualEffect("global", "shadow", alpha=0.1, color="#010203"),
            VisualEffect("other", "shadow", alpha=0.2, color="#040506", target_id="other"),
        ),
    )
    assert tuple(e.effect_id for e in context.effective_effects("target")) == ("global", "__legacy_shadow__")
    assert tuple(e.effect_id for e in context.effective_effects("other")) == ("global", "other", "__legacy_shadow__")


def test_owner_does_not_depend_on_legacy_facade() -> None:
    module = importlib.import_module("visual_engine.runtime.resolution_context")
    assert not any(
        getattr(value, "__module__", "") == "visual_engine.runtime.contract"
        for value in module.__dict__.values()
        if value is not ResolutionContext
    )
