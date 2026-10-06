from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Iterable, Mapping

from visual_engine.components.common.meta import Relation
from visual_engine.runtime.effects import VisualEffect
from visual_engine.runtime.identity import stable_digest
from visual_engine.runtime.graph import RuntimeGraph


# Relation semantics are intentionally data-driven. The hierarchy is not enough to
# express interactions such as HAND --COVERS--> EYE, so a relation may introduce
# a dependency between otherwise unrelated branches of the component tree.
_RELATION_DIRECTIONS: dict[str, str] = {
    "STRUCTURAL": "source_to_target",
    "SPATIAL": "source_to_target",
    "ANATOMICAL": "source_to_target",
    "GEOMETRIC": "source_to_target",
    "CONTACT": "bidirectional",
    "OCCLUSION": "source_to_target",
    "ATTACHMENT": "source_to_target",
    "DEFORMATION": "source_to_target",
    "CAUSAL": "source_to_target",
    "EXPRESSIVE": "source_to_target",
    "SEMANTIC": "source_to_target",
}

_VALID_DIRECTIONS = {"none", "source_to_target", "target_to_source", "bidirectional"}


@dataclass(frozen=True, slots=True)
class RelationDependency:
    """A normalized dependency edge.

    ``dependent_id`` is the component whose resolved result depends on
    ``dependency_id``. ``relation_id`` is deterministic and derived from the
    relation payload rather than Python object identity.
    """

    dependent_id: str
    dependency_id: str
    relation_type: str
    direction: str
    relation_id: str

    def __post_init__(self) -> None:
        if not self.dependent_id or not self.dependency_id:
            raise ValueError("dependency endpoints must be non-empty")
        if not self.relation_type:
            raise ValueError("relation_type must be non-empty")
        if self.direction not in _VALID_DIRECTIONS:
            raise ValueError(f"unsupported relation dependency direction: {self.direction}")
        if not self.relation_id:
            raise ValueError("relation_id must be non-empty")


@dataclass(frozen=True, slots=True)
class RelationDependencyIndex:
    """Indexed relation dependencies for fast invalidation traversal."""

    dependencies_by_dependent: Mapping[str, tuple[RelationDependency, ...]]
    dependents_by_dependency: Mapping[str, tuple[RelationDependency, ...]]

    def dependencies_of(self, component_id: str) -> tuple[RelationDependency, ...]:
        return self.dependencies_by_dependent.get(component_id, ())

    def dependents_of(self, component_id: str) -> tuple[RelationDependency, ...]:
        return self.dependents_by_dependency.get(component_id, ())

    def dependency_closure(self, component_id: str) -> tuple[str, ...]:
        """Return all relation dependencies transitively required by a target.

        The target itself is excluded. Cycles are legal in the relation graph;
        visited-set traversal makes closure deterministic and finite.
        """
        seen: set[str] = {component_id}
        queue: deque[str] = deque([component_id])
        found: set[str] = set()
        while queue:
            current = queue.popleft()
            for edge in self.dependencies_of(current):
                if edge.dependency_id in seen:
                    continue
                seen.add(edge.dependency_id)
                found.add(edge.dependency_id)
                queue.append(edge.dependency_id)
        return tuple(sorted(found))

    def relation_dependency_nodes(self, graph: RuntimeGraph, component_id: str) -> tuple[str, ...]:
        """Return relation dependencies plus their hierarchy ancestors.

        A cross-branch dependency on ``hand`` also depends on the resolved state of
        hand's ancestors because those ancestors can change hand's world transform,
        inherited appearance, z-order or visibility.
        """
        nodes = set(self.dependency_closure(component_id))
        for dependency_id in tuple(nodes):
            current = graph.get(dependency_id)
            while current.parent_id is not None:
                nodes.add(current.parent_id)
                current = graph.get(current.parent_id)
        nodes.discard(component_id)
        return tuple(sorted(nodes))

    def invalidation_path(self, target_id: str, changed_id: str) -> tuple[RelationDependency, ...]:
        """Return one deterministic shortest dependency path, if one exists."""
        if target_id == changed_id:
            return ()
        queue: deque[tuple[str, tuple[RelationDependency, ...]]] = deque([(target_id, ())])
        seen = {target_id}
        while queue:
            current, path = queue.popleft()
            for edge in self.dependencies_of(current):
                next_path = path + (edge,)
                if edge.dependency_id == changed_id:
                    return next_path
                if edge.dependency_id not in seen:
                    seen.add(edge.dependency_id)
                    queue.append((edge.dependency_id, next_path))
        return ()


def relation_direction(relation: Relation) -> str:
    """Resolve relation direction, allowing explicit per-relation overrides.

    ``metadata["dependency_direction"]`` is the only metadata key interpreted by
    this layer. Unknown relation types are intentionally dependency-neutral unless
    a caller explicitly declares a direction; this preserves forward compatibility
    without guessing semantics for arbitrary application-defined relation names.
    """
    override = relation.metadata.get("dependency_direction")
    if override is not None:
        if not isinstance(override, str) or override not in _VALID_DIRECTIONS:
            raise ValueError("metadata.dependency_direction must be a supported direction")
        return override
    return _RELATION_DIRECTIONS.get(relation.relation_type.upper(), "none")


def relation_id(relation: Relation) -> str:
    return stable_digest({
        "source_id": relation.source_id,
        "relation_type": relation.relation_type,
        "target_id": relation.target_id,
        "metadata": relation.metadata,
    })


def build_relation_dependency_index(graph: RuntimeGraph) -> RelationDependencyIndex:
    dependencies: dict[str, list[RelationDependency]] = {}
    dependents: dict[str, list[RelationDependency]] = {}
    for relation in graph.relations:
        direction = relation_direction(relation)
        rid = relation_id(relation)
        pairs: tuple[tuple[str, str], ...]
        if direction == "source_to_target":
            pairs = ((relation.target_id, relation.source_id),)
        elif direction == "target_to_source":
            pairs = ((relation.source_id, relation.target_id),)
        elif direction == "bidirectional":
            pairs = ((relation.target_id, relation.source_id), (relation.source_id, relation.target_id))
        else:
            pairs = ()
        for dependent_id, dependency_id in pairs:
            if dependent_id == dependency_id:
                continue
            edge = RelationDependency(dependent_id, dependency_id, relation.relation_type, direction, rid)
            dependencies.setdefault(dependent_id, []).append(edge)
            dependents.setdefault(dependency_id, []).append(edge)

        # An explicitly declared relation effect is itself a semantic dependency.
        # This closes a subtle invalidation hole when the relation's dependency
        # direction is ``none`` but its effect still changes a visual target.
        if "effect" in relation.metadata:
            effect_target = relation.metadata.get("effect_target", "target")
            if effect_target == "target":
                effect_pairs = ((relation.target_id, relation.source_id),)
            elif effect_target == "source":
                effect_pairs = ((relation.source_id, relation.source_id),)
            elif effect_target is None:
                effect_pairs = tuple((node_id, relation.source_id) for node_id in graph.nodes)
            else:
                raise ValueError("relation metadata.effect_target must be source, target, or null")
            for dependent_id, dependency_id in effect_pairs:
                if dependent_id == dependency_id:
                    continue
                edge = RelationDependency(dependent_id, dependency_id, relation.relation_type, "source_to_target", rid)
                dependencies.setdefault(dependent_id, []).append(edge)
                dependents.setdefault(dependency_id, []).append(edge)

    def ordered(values: Iterable[RelationDependency]) -> tuple[RelationDependency, ...]:
        return tuple(sorted(values, key=lambda e: (e.dependent_id, e.dependency_id, e.relation_type, e.relation_id)))

    return RelationDependencyIndex(
        {k: ordered(v) for k, v in dependencies.items()},
        {k: ordered(v) for k, v in dependents.items()},
    )


def relation_effects(graph: RuntimeGraph, component_id: str) -> tuple[VisualEffect, ...]:
    """Compile optional relation-local effect declarations into visual effects.

    A relation can carry ``metadata["effect"]`` as a mapping accepted by
    ``VisualEffect``. The target defaults to the relation target, while
    ``metadata["effect_target"]`` may select ``source`` or ``target`` explicitly.
    No relation silently becomes an effect: the declaration must be present.
    """
    effects: list[VisualEffect] = []
    for relation in graph.relations:
        declaration = relation.metadata.get("effect")
        if declaration is None:
            continue
        if not isinstance(declaration, Mapping):
            raise ValueError("relation metadata.effect must be a mapping")
        selected_target = relation.metadata.get("effect_target", "target")
        if selected_target == "source":
            target_id = relation.source_id
        elif selected_target == "target":
            target_id = relation.target_id
        elif selected_target is None:
            target_id = None
        else:
            raise ValueError("relation metadata.effect_target must be source, target, or null")
        if target_id != component_id and target_id is not None:
            continue
        payload = dict(declaration)
        payload.setdefault("effect_id", f"relation:{relation_id(relation)}")
        payload.setdefault("source_id", relation.source_id)
        payload.setdefault("target_id", target_id)
        effects.append(VisualEffect(**payload))
    return tuple(sorted(effects, key=lambda e: e.precedence_key))
