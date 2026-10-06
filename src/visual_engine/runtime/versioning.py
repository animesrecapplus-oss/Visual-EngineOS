from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from visual_engine.components.common.meta import Component
from visual_engine.runtime.graph import RuntimeGraph
from visual_engine.runtime.dependencies import build_relation_dependency_index
from visual_engine.runtime.identity import stable_digest
from visual_engine.runtime.version_policy import (
    ENGINE_VERSION,
    SCHEMA_VERSION,
    RESOLUTION_VERSION,
)




@dataclass(frozen=True, slots=True)
class VersionStamp:
    # Defaults are sourced from the canonical policy; explicit values remain allowed
    # for reproducible historical tests and compatibility checks.
    engine: str = ENGINE_VERSION
    schema: str = SCHEMA_VERSION
    resolution: str = RESOLUTION_VERSION

    def __post_init__(self) -> None:
        for name, value in (("engine", self.engine), ("schema", self.schema), ("resolution", self.resolution)):
            if not isinstance(value, str) or not value:
                raise ValueError(f"{name} version must be non-empty")


@dataclass(frozen=True, slots=True)
class ResolutionFingerprint:
    component_id: str
    dependency_digest: str
    version: VersionStamp
    context_digest: str

    @property
    def cache_identity(self) -> str:
        return stable_digest(self)

    def is_compatible_with(self, other: "ResolutionFingerprint") -> bool:
        return self.cache_identity == other.cache_identity


@dataclass(frozen=True, slots=True)
class InvalidationReason:
    changed_component_id: str
    reason: str


def component_fingerprint(component: Component) -> str:
    """Hash all resolution-relevant local data, including nested metadata.

    This is deliberately content-based: direct mutation cannot silently preserve a
    stale dependency token merely because a manual revision counter was forgotten.
    """
    payload = {
        "id": component.id,
        "kind": component.kind,
        "parameters": component.parameters,
        "anchors": component.anchors,
        "relations": component.relations,
        "constraints": component.constraints,
        "profiles": component.profiles,
        "appearance": component.appearance,
        "state": component.state,
        "parent_id": component.parent_id,
        "transform": component.transform,
        "visual": component.visual,
        "visual_overrides": component.visual_overrides,
        "geometry": component.geometry,
    }
    return stable_digest(payload)


def dependency_fingerprint(graph: RuntimeGraph, component_id: str) -> str:
    """Fingerprint hierarchy + semantic relation dependencies transitively.

    Hierarchy dependencies remain ordered because transform/inheritance composition
    is ordered. Relation dependencies are sorted because relation traversal is a
    graph dependency set, not an evaluation order.
    """
    node = graph.get(component_id)
    chain: list[dict[str, str]] = []
    current = node
    while True:
        chain.append({"id": current.id, "fingerprint": component_fingerprint(current.component)})
        if current.parent_id is None:
            break
        current = graph.get(current.parent_id)
    chain.reverse()

    relation_index = build_relation_dependency_index(graph)
    relation_ids = relation_index.relation_dependency_nodes(graph, component_id)
    relation_dependencies = [
        {"id": dependency_id, "fingerprint": component_fingerprint(graph.get(dependency_id).component)}
        for dependency_id in relation_ids
    ]
    return stable_digest({"hierarchy": chain, "relations": relation_dependencies})


def context_fingerprint(context: Any, component_id: str | None = None) -> str:
    """Fingerprint only context that can affect the requested target when known.

    Targeted effects are excluded for unrelated components. State configuration is
    narrowed to active state names. This prevents a shared scene context from
    invalidating every sibling merely because one sibling received a new effect.
    """
    if component_id is None:
        return stable_digest(context)
    effects = tuple(
        effect for effect in context.effects
        if effect.target_id is None or effect.target_id == component_id
    )
    active = set(context.active_states)
    groups = tuple(item for item in context.state_groups if item[0] in active)
    conflicts = tuple(item for item in context.state_conflicts if item[0] in active)
    requires = tuple(item for item in context.state_requires if item[0] in active)
    payload = {
        "shadow_alpha": context.shadow_alpha,
        "shadow_color": context.shadow_color,
        "occluded_by": context.occluded_by,
        "active_states": context.active_states,
        # A context priority with no active context state cannot affect the
        # resolver. Excluding it prevents a false cache miss while retaining
        # the value whenever it can participate in state precedence.
        "state_priority": context.state_priority if context.active_states else None,
        "state_groups": groups,
        "state_conflicts": conflicts,
        "state_requires": requires,
        "consequence_states": tuple(context.consequence_states),
        "effects": effects,
    }
    return stable_digest(payload)


def resolution_fingerprint(graph: RuntimeGraph, component_id: str, context: Any, version: VersionStamp | None = None) -> ResolutionFingerprint:
    version = version or VersionStamp()
    return ResolutionFingerprint(component_id, dependency_fingerprint(graph, component_id), version, context_fingerprint(context, component_id))


def invalidation_reasons(graph: RuntimeGraph, component_id: str, changed_component_id: str) -> tuple[InvalidationReason, ...]:
    """Explain hierarchy or semantic-relation invalidation for a target."""
    node = graph.get(component_id)
    current = node
    ancestors: set[str] = set()
    while True:
        ancestors.add(current.id)
        if current.parent_id is None:
            break
        current = graph.get(current.parent_id)
    reasons: list[InvalidationReason] = []
    if changed_component_id in ancestors:
        reasons.append(InvalidationReason(changed_component_id, "ancestor-or-self affects resolved transform/visual dependency"))

    relation_index = build_relation_dependency_index(graph)
    relation_ids = set(relation_index.relation_dependency_nodes(graph, component_id))
    if changed_component_id in relation_ids:
        path = relation_index.invalidation_path(component_id, changed_component_id)
        relation_chain = " -> ".join(edge.relation_type for edge in path) if path else "relation-dependency"
        reasons.append(InvalidationReason(
            changed_component_id,
            f"semantic relation dependency affects target via {relation_chain}",
        ))
    else:
        # A relation dependency can itself be hierarchically affected. Find the
        # nearest relation dependency whose ancestor chain contains the change.
        for dependency_id in sorted(relation_index.dependency_closure(component_id)):
            current = graph.get(dependency_id)
            while current.parent_id is not None:
                if current.parent_id == changed_component_id:
                    path = relation_index.invalidation_path(component_id, dependency_id)
                    relation_chain = " -> ".join(edge.relation_type for edge in path) if path else "relation-dependency"
                    reasons.append(InvalidationReason(
                        changed_component_id,
                        f"ancestor of semantic relation dependency {dependency_id} affects target via {relation_chain}",
                    ))
                    return tuple(reasons)
                current = graph.get(current.parent_id)
    return tuple(reasons)
