from __future__ import annotations

from typing import Iterable

from visual_engine.components.common.meta import Component


from visual_engine.runtime.state_policy_contract import StateActivation, StateDecision


def _validate_names(values: Iterable[str], field: str) -> tuple[str, ...]:
    result = tuple(values)
    if any(not isinstance(v, str) or not v for v in result):
        raise ValueError(f"{field} entries must be non-empty strings")
    if len(set(result)) != len(result):
        raise ValueError(f"{field} entries must be unique")
    return result


def collect_state_activations(
    chain: tuple[Component, ...],
    active_states: tuple[str, ...],
    *,
    context_priority: int = 1000,
    context_groups: dict[str, str] | None = None,
    context_conflicts: dict[str, tuple[str, ...]] | None = None,
    context_requires: dict[str, tuple[str, ...]] | None = None,
) -> tuple[StateActivation, ...]:
    """Collect state candidates without resolving conflicts."""
    context_groups = context_groups or {}
    context_conflicts = context_conflicts or {}
    context_requires = context_requires or {}
    candidates: list[StateActivation] = []
    for name in _validate_names(active_states, "active_states"):
        candidates.append(StateActivation(
            name=name,
            source_id="__context__",
            priority=context_priority,
            specificity=len(chain),
            group=context_groups.get(name),
            conflicts=_validate_names(context_conflicts.get(name, ()), f"context conflict {name}"),
            requires=_validate_names(context_requires.get(name, ()), f"context requirement {name}"),
            source_rank=2,
        ))
    for index, component in enumerate(chain):
        for layer in component.state:
            if not layer.enabled:
                continue
            candidates.append(StateActivation(
                name=layer.name,
                source_id=component.id,
                priority=layer.priority,
                specificity=index,
                group=layer.group,
                conflicts=layer.conflicts,
                requires=layer.requires,
                source_rank=1,
            ))
    return tuple(candidates)


def resolve_state_activations_with_decisions(candidates: tuple[StateActivation, ...]) -> tuple[tuple[StateActivation, ...], tuple[StateDecision, ...]]:
    """Resolve state precedence and retain a complete audit trail.

    The audit trail deliberately records *why* candidates were rejected. This is
    essential once state graphs become large: ``active_states`` alone cannot explain
    whether a state lost to a group, an explicit conflict, or a missing requirement.
    """
    ordered = sorted(candidates, key=lambda c: c.precedence_key, reverse=True)
    # A logical state may be contributed by several ancestors. Resolve it once so
    # inherited state metadata cannot accidentally create duplicate activations.
    by_name: dict[str, StateActivation] = {}
    decisions: list[StateDecision] = []
    for candidate in ordered:
        winner = by_name.get(candidate.name)
        if winner is None:
            by_name[candidate.name] = candidate
        else:
            decisions.append(StateDecision(candidate, "reject", f"duplicate state name won by {winner.source_id}"))
    ordered = sorted(by_name.values(), key=lambda c: c.precedence_key, reverse=True)
    accepted: list[StateActivation] = []
    occupied_groups: dict[str, StateActivation] = {}
    for candidate in ordered:
        if candidate.group is not None and candidate.group in occupied_groups:
            winner = occupied_groups[candidate.group]
            decisions.append(StateDecision(candidate, "reject", f"exclusive group '{candidate.group}' won by {winner.name}"))
            continue
        conflict = next((current for current in accepted if candidate.name in current.conflicts or current.name in candidate.conflicts), None)
        if conflict is not None:
            decisions.append(StateDecision(candidate, "reject", f"conflicts with higher-precedence {conflict.name}"))
            continue
        accepted.append(candidate)
        if candidate.group is not None:
            occupied_groups[candidate.group] = candidate
        decisions.append(StateDecision(candidate, "accept", "passed group/conflict precedence"))

    changed = True
    while changed:
        changed = False
        names = {item.name for item in accepted}
        kept: list[StateActivation] = []
        for item in accepted:
            missing = tuple(required for required in item.requires if required not in names)
            if missing:
                decisions.append(StateDecision(item, "reject", f"missing required states: {', '.join(missing)}"))
                changed = True
                continue
            kept.append(item)
        accepted = kept
    accepted = sorted(accepted, key=lambda c: (c.name, c.source_id))
    return tuple(accepted), tuple(decisions)


def resolve_state_activations(candidates: tuple[StateActivation, ...]) -> tuple[StateActivation, ...]:
    return resolve_state_activations_with_decisions(candidates)[0]


def resolve_states_with_decisions(
    chain: tuple[Component, ...],
    active_states: tuple[str, ...],
    *,
    context_priority: int = 1000,
    context_groups: dict[str, str] | None = None,
    context_conflicts: dict[str, tuple[str, ...]] | None = None,
    context_requires: dict[str, tuple[str, ...]] | None = None,
) -> tuple[tuple[StateActivation, ...], tuple[StateDecision, ...]]:
    candidates = collect_state_activations(
        chain, active_states,
        context_priority=context_priority,
        context_groups=context_groups,
        context_conflicts=context_conflicts,
        context_requires=context_requires,
    )
    return resolve_state_activations_with_decisions(candidates)


def resolve_states(
    chain: tuple[Component, ...],
    active_states: tuple[str, ...],
    **kwargs,
) -> tuple[StateActivation, ...]:
    return resolve_states_with_decisions(chain, active_states, **kwargs)[0]
