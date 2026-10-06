from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from types import MappingProxyType
from typing import Mapping

from visual_engine.components.common.meta import Component, Relation


@dataclass(frozen=True, slots=True)
class RuntimeNode:
    id: str
    kind: str
    parent_id: str | None
    component: Component


def _collect_components(root: Component) -> tuple[Component, ...]:
    """Traverse the authoring tree defensively before compiling runtime indexes.

    ``Component`` is intentionally mutable, so callers can temporarily construct
    invalid topology. Runtime compilation must reject a cycle rather than allowing
    ``Component.walk()`` to recurse forever, and it must verify that each child
    agrees with the parent pointer used by the runtime index.
    """
    components: list[Component] = []
    active_objects: set[int] = set()
    seen_objects: set[int] = set()

    def visit(component: Component, expected_parent_id: str | None) -> None:
        object_id = id(component)
        if object_id in active_objects:
            raise ValueError("Cycle in component hierarchy")
        if object_id in seen_objects:
            raise ValueError("Component object appears more than once in hierarchy")
        if component.parent_id != expected_parent_id:
            raise ValueError(
                f"Parent link mismatch for component {component.id}: "
                f"expected {expected_parent_id!r}, got {component.parent_id!r}"
            )

        active_objects.add(object_id)
        seen_objects.add(object_id)
        components.append(component)
        for child in component.children:
            visit(child, component.id)
        active_objects.remove(object_id)

    visit(root, None)
    return tuple(components)


def _structural_digest(root: Component) -> str:
    """Return a deterministic digest of graph topology and relation endpoints.

    RuntimeGraph is an index over a mutable authoring tree. The digest makes that
    lifecycle explicit: topology/relation mutation after graph compilation cannot
    silently leave stale indexes in use. Local visual/geometry mutation does not
    alter topology and remains the responsibility of the resolution/cache layer.
    """
    components = _collect_components(root)
    nodes = []
    relations = []
    for component in components:
        nodes.append((component.id, component.kind, component.parent_id, tuple(child.id for child in component.children)))
        relations.extend((r.source_id, r.relation_type, r.target_id) for r in component.relations)
    payload = {"nodes": nodes, "relations": sorted(relations)}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True, slots=True)
class RuntimeGraph:
    """Validated, read-only topology index over an authoring Component tree.

    Components remain mutable by design.  A graph is therefore a compiled view,
    not an ownership transfer.  If hierarchy or relation topology changes, call
    :meth:`rebuild` and use the returned graph.  Direct mutation of graph indexes
    is prevented by immutable mapping/tuple containers.
    """

    _nodes: Mapping[str, RuntimeNode] = field(default_factory=dict, repr=False)
    _relations: tuple[Relation, ...] = field(default_factory=tuple, repr=False)
    _children_index: Mapping[str, tuple[str, ...]] = field(default_factory=dict, repr=False)
    _relations_by_source: Mapping[str, tuple[Relation, ...]] = field(default_factory=dict, repr=False)
    _relations_by_target: Mapping[str, tuple[Relation, ...]] = field(default_factory=dict, repr=False)
    _root: Component | None = field(default=None, repr=False, compare=False)
    _structural_digest: str = field(default="", repr=False, compare=False)

    @classmethod
    def from_component(cls, root: Component) -> "RuntimeGraph":
        nodes: dict[str, RuntimeNode] = {}
        relations: list[Relation] = []
        # Compile from the defensive traversal rather than Component.walk(); a malformed
        # authoring cycle must become a deterministic validation error, never recursion.
        for component in _collect_components(root):
            if component.id in nodes:
                raise ValueError(f"Duplicate component id: {component.id}")
            nodes[component.id] = RuntimeNode(component.id, component.kind, component.parent_id, component)
            relations.extend(component.relations)

        graph = cls(_nodes=nodes, _relations=tuple(relations), _root=root)
        graph._validate_parent_links()
        graph._validate_acyclic_hierarchy()
        graph._validate_relations()

        children: dict[str, list[str]] = {}
        by_source: dict[str, list[Relation]] = {}
        by_target: dict[str, list[Relation]] = {}
        for node in nodes.values():
            if node.parent_id is not None:
                children.setdefault(node.parent_id, []).append(node.id)
        for relation in relations:
            by_source.setdefault(relation.source_id, []).append(relation)
            by_target.setdefault(relation.target_id, []).append(relation)

        return cls(
            _nodes=MappingProxyType(dict(nodes)),
            _relations=tuple(relations),
            _children_index=MappingProxyType({k: tuple(v) for k, v in children.items()}),
            _relations_by_source=MappingProxyType({k: tuple(v) for k, v in by_source.items()}),
            _relations_by_target=MappingProxyType({k: tuple(v) for k, v in by_target.items()}),
            _root=root,
            _structural_digest=_structural_digest(root),
        )

    def _assert_current(self) -> None:
        if self._root is None:
            return
        current = _structural_digest(self._root)
        if current != self._structural_digest:
            raise RuntimeError(
                "RuntimeGraph is stale: component hierarchy or relation topology changed; "
                "rebuild the graph before querying it"
            )

    def rebuild(self) -> "RuntimeGraph":
        """Compile a fresh graph from the same authoring root."""
        if self._root is None:
            raise RuntimeError("RuntimeGraph has no authoring root")
        return type(self).from_component(self._root)

    def is_current(self) -> bool:
        """Return whether the compiled indexes still match the authoring topology."""
        return self._root is None or _structural_digest(self._root) == self._structural_digest

    def _validate_parent_links(self) -> None:
        for node in self._nodes.values():
            if node.parent_id is not None and node.parent_id not in self._nodes:
                raise ValueError(f"Missing parent: {node.parent_id}")

    def _validate_acyclic_hierarchy(self) -> None:
        for node in self._nodes.values():
            seen: set[str] = set()
            current = node
            while current.parent_id is not None:
                if current.id in seen:
                    raise ValueError("Cycle in component hierarchy")
                seen.add(current.id)
                current = self._nodes[current.parent_id]

    def _validate_relations(self) -> None:
        for relation in self._relations:
            if relation.source_id not in self._nodes or relation.target_id not in self._nodes:
                raise ValueError("Relation references unknown component")

    @property
    def nodes(self) -> Mapping[str, RuntimeNode]:
        self._assert_current()
        return self._nodes

    @property
    def relations(self) -> tuple[Relation, ...]:
        self._assert_current()
        return self._relations

    @property
    def children_index(self) -> Mapping[str, tuple[str, ...]]:
        self._assert_current()
        return self._children_index

    @property
    def relations_by_source(self) -> Mapping[str, tuple[Relation, ...]]:
        self._assert_current()
        return self._relations_by_source

    @property
    def relations_by_target(self) -> Mapping[str, tuple[Relation, ...]]:
        self._assert_current()
        return self._relations_by_target

    def get(self, component_id: str) -> RuntimeNode:
        self._assert_current()
        return self._nodes[component_id]

    def children_of(self, component_id: str) -> tuple[RuntimeNode, ...]:
        self._assert_current()
        return tuple(self._nodes[i] for i in self._children_index.get(component_id, ()))

    def descendants_of(self, component_id: str) -> tuple[RuntimeNode, ...]:
        self._assert_current()
        return tuple(n for n in self._nodes.values() if self._is_descendant(n.id, component_id))

    def _is_descendant(self, candidate: str, ancestor: str) -> bool:
        current = self._nodes[candidate]
        while current.parent_id is not None:
            if current.parent_id == ancestor:
                return True
            current = self._nodes[current.parent_id]
        return False
