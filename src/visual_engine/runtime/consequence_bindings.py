from __future__ import annotations

"""Declarative bridge from resolved consequences to existing state/effect contracts.

This module translates semantic consequence names; it does not resolve or mutate
component state and it does not render. The existing state/effect policy engines
remain the sole owners of precedence/composition semantics.
"""

from dataclasses import dataclass, replace
from typing import Mapping

from visual_engine.runtime.consequence_aggregation import ConsequenceAggregationResult, ResolvedConsequence
from visual_engine.runtime.effects import VisualEffect
from visual_engine.runtime.state_policy import StateActivation


@dataclass(frozen=True, slots=True)
class StateConsequenceBinding:
    consequence: str
    state_name: str
    priority_offset: int = 0
    group: str | None = None
    conflicts: tuple[str, ...] = ()
    requires: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.consequence or not self.state_name:
            raise ValueError("state consequence binding identifiers are required")
        if not isinstance(self.priority_offset, int):
            raise ValueError("state priority_offset must be an integer")
        if self.group is not None and not self.group:
            raise ValueError("state binding group must be non-empty")
        for name, values in (("conflicts", self.conflicts), ("requires", self.requires)):
            if any(not isinstance(v, str) or not v for v in values):
                raise ValueError(f"state binding {name} entries must be non-empty")
            if len(set(values)) != len(values):
                raise ValueError(f"state binding {name} entries must be unique")
            if self.state_name in values:
                raise ValueError(f"state binding {name} cannot contain its own state")


@dataclass(frozen=True, slots=True)
class EffectConsequenceBinding:
    consequence: str
    kind: str
    priority_offset: int = 0
    alpha: float = 0.0
    color: str = "#000000"
    opacity_factor: float = 1.0
    visibility_factor: float = 1.0

    def __post_init__(self) -> None:
        if not self.consequence:
            raise ValueError("effect consequence binding identifier is required")
        if not isinstance(self.priority_offset, int):
            raise ValueError("effect priority_offset must be an integer")
        # Let VisualEffect remain the canonical validator for effect values.
        VisualEffect(
            effect_id="__binding_validation__", kind=self.kind, priority=self.priority_offset,
            alpha=self.alpha, color=self.color, opacity_factor=self.opacity_factor,
            visibility_factor=self.visibility_factor,
        )


@dataclass(frozen=True, slots=True)
class ConsequenceBindingSet:
    states: tuple[StateConsequenceBinding, ...] = ()
    effects: tuple[EffectConsequenceBinding, ...] = ()

    def __post_init__(self) -> None:
        state_keys = [x.consequence for x in self.states]
        effect_keys = [x.consequence for x in self.effects]
        if len(state_keys) != len(set(state_keys)):
            raise ValueError("duplicate state consequence bindings")
        if len(effect_keys) != len(set(effect_keys)):
            raise ValueError("duplicate effect consequence bindings")

    def state_map(self) -> dict[str, StateConsequenceBinding]:
        return {x.consequence: x for x in self.states}

    def effect_map(self) -> dict[str, EffectConsequenceBinding]:
        return {x.consequence: x for x in self.effects}


@dataclass(frozen=True, slots=True)
class ConsequenceBindingResult:
    target_id: str
    states: tuple[StateActivation, ...]
    effects: tuple[VisualEffect, ...]
    unbound: tuple[ResolvedConsequence, ...]


def _payload_value(request: ResolvedConsequence, key: str, default: str) -> str:
    return request.request.payload.get(key, default)


def compile_resolved_consequences(
    result: ConsequenceAggregationResult,
    bindings: ConsequenceBindingSet,
) -> ConsequenceBindingResult:
    """Compile accepted consequences into the *existing* state/effect envelopes.

    The compiler is deliberately one-way and loss-aware: an accepted request
    with no explicit binding is returned in ``unbound`` rather than guessed into
    a state or effect. State precedence is left to ``state_policy`` and effect
    composition to ``effects``.
    """
    state_map = bindings.state_map()
    effect_map = bindings.effect_map()
    states: list[StateActivation] = []
    effects: list[VisualEffect] = []
    unbound: list[ResolvedConsequence] = []

    for item in result.resolved:
        request = item.request
        consequence = request.payload.get("consequence", "")
        if request.kind.value == "state":
            binding = state_map.get(consequence)
            if binding is None:
                unbound.append(item)
                continue
            states.append(StateActivation(
                name=binding.state_name,
                source_id=f"consequence:{item.fingerprint}",
                priority=request.precedence + binding.priority_offset,
                specificity=1,
                group=binding.group,
                conflicts=binding.conflicts,
                requires=binding.requires,
                source_rank=1,
            ))
        elif request.kind.value == "effect":
            binding = effect_map.get(consequence)
            if binding is None:
                unbound.append(item)
                continue
            effects.append(VisualEffect(
                effect_id=f"consequence:{item.fingerprint}",
                kind=binding.kind,
                priority=request.precedence + binding.priority_offset,
                alpha=binding.alpha,
                color=binding.color,
                opacity_factor=binding.opacity_factor,
                visibility_factor=binding.visibility_factor,
                source_id=request.source_event_key[2],
                target_id=request.target_id,
                metadata=(
                    ("consequence", consequence),
                    ("region_id", request.region_id),
                    ("request_fingerprint", item.fingerprint),
                ),
            ))
        else:
            # Geometry and appearance intentionally remain unbound here. Their
            # resolvers need dedicated contracts rather than a guessed mutation.
            unbound.append(item)

    states.sort(key=lambda x: x.precedence_key, reverse=True)
    effects.sort(key=lambda x: x.precedence_key)
    return ConsequenceBindingResult(result.target_id, tuple(states), tuple(effects), tuple(unbound))


def apply_consequence_binding_result(
    context,
    result: ConsequenceBindingResult,
):
    """Attach target-scoped consequence outputs to an immutable resolution context.

    This is the boundary between consequence semantics and component resolution.
    It never resolves conflicts itself: state activations are consumed by the
    existing state policy and visual effects by the existing effect policy.
    Geometry and appearance consequences remain unbound.
    """
    from visual_engine.runtime.contract import ResolutionContext

    if not isinstance(context, ResolutionContext):
        raise TypeError("context must be a ResolutionContext")
    if result.target_id and any(
        effect.target_id not in (None, result.target_id) for effect in result.effects
    ):
        raise ValueError("binding result contains an effect targeting another component")
    effects = context.effects + result.effects
    effect_ids = [effect.effect_id for effect in effects]
    if len(effect_ids) != len(set(effect_ids)):
        raise ValueError("consequence binding would introduce duplicate effect IDs")
    return replace(
        context,
        consequence_states=context.consequence_states + result.states,
        effects=effects,
    )
