from __future__ import annotations

"""Explicit resolution of ``Component.appearance`` into typed contributions.

The legacy ``AppearanceLayer`` model intentionally has no implicit inheritance,
priority, domain or state semantics. This module therefore requires an explicit
binding contract before a layer can become an ``AppearanceContribution``.
It is a resolver boundary, not a color/material/lighting engine.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from visual_engine.components.common.meta import AppearanceLayer, Component
from visual_engine.runtime.appearance_contract import AppearanceContribution, AppearanceDomain
from visual_engine.runtime.effects import VisualEffect
from visual_engine.runtime.versioning import stable_digest


class LayerActivationMode(str, Enum):
    ALL_STATES = "all_states"
    ANY_STATE = "any_state"


class LayerConflictMode(str, Enum):
    KEEP_ALL = "keep_all"
    HIGHEST_PRIORITY = "highest_priority"
    REJECT_CONFLICT = "reject_conflict"


@dataclass(frozen=True, slots=True)
class AppearanceLayerBinding:
    """Explicit semantic binding for one existing local appearance layer.

    ``order`` controls contribution order. If omitted, the declaration index in
    ``Component.appearance`` is used. ``priority`` is only used by an explicit
    conflict policy; it never silently overrides layer order.
    """

    layer_name: str
    domain: AppearanceDomain
    priority: int = 0
    order: int | None = None
    required_states: tuple[str, ...] = ()
    activation_mode: LayerActivationMode = LayerActivationMode.ALL_STATES
    conflict_group: str | None = None

    def __post_init__(self) -> None:
        if not self.layer_name:
            raise ValueError("appearance layer binding name is required")
        if not isinstance(self.priority, int):
            raise ValueError("appearance layer binding priority must be an integer")
        if self.order is not None and not isinstance(self.order, int):
            raise ValueError("appearance layer binding order must be an integer")
        states = tuple(sorted(set(self.required_states)))
        if any(not isinstance(v, str) or not v for v in states):
            raise ValueError("required appearance states must be non-empty strings")
        object.__setattr__(self, "required_states", states)
        if self.conflict_group is not None and not self.conflict_group:
            raise ValueError("appearance conflict_group must be non-empty")


@dataclass(frozen=True, slots=True)
class AppearanceLayerPolicy:
    """Conflict policy for an explicitly declared layer group."""

    group: str
    mode: LayerConflictMode = LayerConflictMode.KEEP_ALL

    def __post_init__(self) -> None:
        if not self.group:
            raise ValueError("appearance layer policy group is required")


@dataclass(frozen=True, slots=True)
class AppearanceLayerProvenance:
    contribution_id: str
    source_component_id: str
    layer_name: str | None
    source_kind: str
    domain: AppearanceDomain
    order: int
    priority: int
    active_states: tuple[str, ...]
    fingerprint: str


@dataclass(frozen=True, slots=True)
class AppearanceLayerDecision:
    contribution_id: str
    action: str
    reason: str
    conflicting_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class AppearanceLayerResolution:
    target_id: str
    contributions: tuple[AppearanceContribution, ...]
    provenance: tuple[AppearanceLayerProvenance, ...]
    decisions: tuple[AppearanceLayerDecision, ...]
    unresolved_layers: tuple[str, ...]
    dependency_digest: str


def _values_tuple(values: dict[str, Any]) -> tuple[tuple[str, Any], ...]:
    return tuple(sorted(values.items(), key=lambda item: item[0]))


def _active(binding: AppearanceLayerBinding, active_states: set[str]) -> bool:
    required = set(binding.required_states)
    if not required:
        return True
    if binding.activation_mode is LayerActivationMode.ALL_STATES:
        return required.issubset(active_states)
    if binding.activation_mode is LayerActivationMode.ANY_STATE:
        return bool(required & active_states)
    raise ValueError(f"unsupported appearance layer activation mode: {binding.activation_mode}")


def _layer_fingerprint(
    component: Component,
    layers: tuple[AppearanceLayer, ...],
    bindings: tuple[AppearanceLayerBinding, ...],
    policies: tuple[AppearanceLayerPolicy, ...],
    active_states: tuple[str, ...],
    effects: tuple[VisualEffect, ...],
) -> str:
    return stable_digest({
        "component_id": component.id,
        "appearance": layers,
        "bindings": bindings,
        "policies": policies,
        "active_states": active_states,
        "effects": effects,
    })


def resolve_appearance_layers(
    component: Component,
    *,
    active_states: Iterable[str] = (),
    effects: Iterable[VisualEffect] = (),
    bindings: Iterable[AppearanceLayerBinding] = (),
    policies: Iterable[AppearanceLayerPolicy] = (),
) -> AppearanceLayerResolution:
    """Resolve local appearance layers without inventing hierarchy semantics.

    Only ``component.appearance`` is considered. Parent/ancestor appearance is
    deliberately not traversed. A layer without an explicit binding is reported
    as unresolved instead of being guessed into a domain.

    Effects are already typed by ``VisualEffect`` and therefore become typed
    EFFECT contributions directly; their visual meaning is not reinterpreted.
    Active states only activate layers through explicit ``required_states``.
    """
    layers = tuple(component.appearance)
    binding_list = tuple(sorted(bindings, key=lambda b: (b.layer_name, b.domain.value, b.order if b.order is not None else 2**31 - 1, b.priority)))
    policy_list = tuple(sorted(policies, key=lambda p: p.group))
    state_names = tuple(sorted(set(active_states)))
    if any(not isinstance(value, str) or not value for value in state_names):
        raise ValueError("active appearance states must be non-empty strings")
    if any(not isinstance(layer, AppearanceLayer) for layer in layers):
        raise ValueError("component.appearance must contain AppearanceLayer instances")

    binding_map: dict[str, AppearanceLayerBinding] = {}
    for binding in binding_list:
        if binding.layer_name in binding_map:
            raise ValueError(f"duplicate appearance layer binding: {binding.layer_name}")
        binding_map[binding.layer_name] = binding
    policy_map: dict[str, AppearanceLayerPolicy] = {}
    for policy in policy_list:
        if policy.group in policy_map:
            raise ValueError(f"duplicate appearance layer policy group: {policy.group}")
        policy_map[policy.group] = policy

    # Layer names are the only identity exposed by the legacy model. Duplicate
    # names are therefore ambiguous at this boundary and fail closed.
    names = [layer.name for layer in layers]
    if len(names) != len(set(names)):
        raise ValueError("duplicate Component.appearance layer names are ambiguous")

    contributions: list[AppearanceContribution] = []
    provenance: list[AppearanceLayerProvenance] = []
    decisions: list[AppearanceLayerDecision] = []
    unresolved: list[str] = []
    active_set = set(state_names)

    for declaration_index, layer in enumerate(layers):
        binding = binding_map.get(layer.name)
        if binding is None:
            unresolved.append(layer.name)
            decisions.append(AppearanceLayerDecision(
                f"layer:{component.id}:{layer.name}", "unresolved", "missing explicit binding"
            ))
            continue
        if not _active(binding, active_set):
            decisions.append(AppearanceLayerDecision(
                f"layer:{component.id}:{layer.name}", "inactive", "required active-state condition not satisfied"
            ))
            continue
        order = binding.order if binding.order is not None else declaration_index
        contribution_id = f"layer:{component.id}:{layer.name}"
        contribution = AppearanceContribution(
            contribution_id=contribution_id,
            domain=binding.domain,
            source_id=component.id,
            values=_values_tuple(layer.values),
            opacity=layer.opacity,
        )
        fingerprint = stable_digest({
            "component_id": component.id,
            "layer": layer,
            "binding": binding,
            "active_states": state_names,
        })
        contributions.append(contribution)
        provenance.append(AppearanceLayerProvenance(
            contribution_id, component.id, layer.name, "component.appearance",
            binding.domain, order, binding.priority, state_names, fingerprint,
        ))

    # Effects are typed inputs, not inferred layer names. Only effects explicitly
    # targeting this component (or globally applicable effects) are accepted.
    effect_list = tuple(sorted(effects, key=lambda effect: effect.precedence_key))
    effect_ids = [effect.effect_id for effect in effect_list]
    if len(effect_ids) != len(set(effect_ids)):
        raise ValueError("duplicate visual effect IDs are ambiguous at appearance boundary")
    for effect in effect_list:
        if effect.target_id not in (None, component.id):
            continue
        contribution_id = f"effect:{effect.effect_id}"
        contribution = AppearanceContribution(
            contribution_id=contribution_id,
            domain=AppearanceDomain.EFFECT,
            source_id=effect.source_id,
            values=(
                ("alpha", effect.alpha),
                ("color", effect.color),
                ("effect_id", effect.effect_id),
                ("kind", effect.kind),
                ("metadata", effect.metadata),
                ("opacity_factor", effect.opacity_factor),
                ("priority", effect.priority),
                ("source_id", effect.source_id),
                ("target_id", effect.target_id),
                ("visibility_factor", effect.visibility_factor),
            ),
        )
        fingerprint = stable_digest({"effect": effect, "component_id": component.id})
        contributions.append(contribution)
        provenance.append(AppearanceLayerProvenance(
            contribution_id, component.id, None, "visual_effect",
            AppearanceDomain.EFFECT, effect.priority, effect.priority, state_names, fingerprint,
        ))

    # Explicit layer conflicts are resolved before final ordering. Effects have no
    # implicit conflict group here; their existing effect policy remains authoritative.
    by_group: dict[str, list[int]] = {}
    for index, item in enumerate(provenance):
        if item.layer_name is not None:
            binding = binding_map[item.layer_name]
            if binding.conflict_group is not None:
                if binding.conflict_group not in policy_map:
                    raise ValueError(f"appearance conflict group has no policy: {binding.conflict_group}")
                by_group.setdefault(binding.conflict_group, []).append(index)

    rejected_ids: set[str] = set()
    for group, indices in sorted(by_group.items()):
        policy = policy_map[group]
        if len(indices) <= 1:
            continue
        ids = tuple(sorted(provenance[i].contribution_id for i in indices))
        if policy.mode is LayerConflictMode.KEEP_ALL:
            continue
        if policy.mode is LayerConflictMode.REJECT_CONFLICT:
            rejected_ids.update(ids)
            for identifier in ids:
                decisions.append(AppearanceLayerDecision(identifier, "rejected", f"conflict group '{group}'", tuple(x for x in ids if x != identifier)))
        elif policy.mode is LayerConflictMode.HIGHEST_PRIORITY:
            winner_index = max(indices, key=lambda i: (provenance[i].priority, -provenance[i].order, provenance[i].contribution_id))
            winner = provenance[winner_index].contribution_id
            for index in indices:
                identifier = provenance[index].contribution_id
                if identifier != winner:
                    rejected_ids.add(identifier)
                    decisions.append(AppearanceLayerDecision(identifier, "rejected", f"precedence in conflict group '{group}'", tuple(x for x in ids if x != identifier)))
                else:
                    decisions.append(AppearanceLayerDecision(identifier, "accepted", f"highest priority in conflict group '{group}'", tuple(x for x in ids if x != identifier)))
        else:
            raise ValueError(f"unsupported appearance conflict mode: {policy.mode}")

    accepted_pairs = [
        (contribution, source)
        for contribution, source in zip(contributions, provenance)
        if contribution.contribution_id not in rejected_ids
    ]
    accepted_pairs.sort(key=lambda pair: (pair[1].order, pair[1].priority, pair[0].contribution_id))
    final_contributions = tuple(item[0] for item in accepted_pairs)
    final_provenance = tuple(item[1] for item in accepted_pairs)

    decisions.extend(
        AppearanceLayerDecision(item.contribution_id, "accepted", "explicit binding and activation satisfied")
        for item in final_provenance
        if not any(d.contribution_id == item.contribution_id for d in decisions)
    )
    decisions = sorted(decisions, key=lambda d: (d.contribution_id, d.action, d.reason))
    dependency_digest = _layer_fingerprint(component, layers, binding_list, policy_list, state_names, effect_list)
    return AppearanceLayerResolution(
        component.id, final_contributions, final_provenance, tuple(decisions), tuple(sorted(unresolved)), dependency_digest
    )
