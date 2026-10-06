from __future__ import annotations
from collections import OrderedDict
from dataclasses import dataclass, fields, is_dataclass
from enum import Enum
import math
from threading import Event, RLock
from typing import Any, Callable, Iterable, Mapping
import json
from visual_engine.components.common.meta import Component
from visual_engine.components.common.geometry_contract import GeometryContract, canonical_geometry_payload, geometry_hash
from visual_engine.runtime.graph import RuntimeGraph
from visual_engine.runtime.versioning import VersionStamp, stable_digest
from visual_engine.runtime.dependencies import build_relation_dependency_index, relation_direction

@dataclass(frozen=True, slots=True)
class GeometryCacheKey:
    component_id: str
    dependency_digest: str
    geometry_input_digest: str
    generator: str
    generator_version: str
    version: VersionStamp

    def __post_init__(self) -> None:
        # Cache keys are durable identity values, not arbitrary tuples. Rejecting
        # malformed fields here prevents ambiguous entries from entering the LRU.
        for name, value in (
            ("component_id", self.component_id),
            ("dependency_digest", self.dependency_digest),
            ("geometry_input_digest", self.geometry_input_digest),
            ("generator", self.generator),
            ("generator_version", self.generator_version),
        ):
            if not isinstance(value, str) or not value:
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.version, VersionStamp):
            raise TypeError("version must be a VersionStamp")

    @property
    def cache_identity(self) -> str:
        return stable_digest(self)

@dataclass(frozen=True, slots=True)
class GeometryCacheEntry:
    key: GeometryCacheKey
    geometry: GeometryContract
    geometry_digest: str
    dependency_ids: tuple[str, ...]
    size_bytes: int

@dataclass(frozen=True, slots=True)
class GeometryCacheStats:
    hits: int
    misses: int
    builds: int
    evictions: int
    invalidations: int
    entries: int
    bytes: int

@dataclass(slots=True)
class _Inflight:
    event: Event
    error: BaseException | None = None

GEOMETRY_FINGERPRINT_CONTRACT_VERSION = "1"
GEOMETRY_FINGERPRINT_ALGORITHM = "sha256"


def _validate_fingerprint_value(value: Any, *, path: str = "value", seen: set[int] | None = None) -> None:
    """Validate the value domain before it enters a geometry cache identity.

    Geometry cache identity must be deterministic.  In particular, arbitrary Python
    objects, sets, non-string mapping keys and non-finite floats are not accepted:
    relying on their repr/order would make cache identity dependent on process state.
    ``stable_digest`` already rejects many of these cases, but this explicit boundary
    gives callers a deterministic contract and a useful error at the cache boundary.
    """
    if seen is None:
        seen = set()
    if value is None or isinstance(value, (bool, str, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"non-finite geometry fingerprint value at {path}")
        return
    if isinstance(value, Enum):
        _validate_fingerprint_value(value.value, path=f"{path}.value", seen=seen)
        return
    if is_dataclass(value):
        marker = id(value)
        if marker in seen:
            raise ValueError(f"cyclic geometry fingerprint value at {path}")
        seen.add(marker)
        try:
            for field in fields(value):
                _validate_fingerprint_value(getattr(value, field.name), path=f"{path}.{field.name}", seen=seen)
        finally:
            seen.remove(marker)
        return
    if isinstance(value, Mapping):
        marker = id(value)
        if marker in seen:
            raise ValueError(f"cyclic geometry fingerprint mapping at {path}")
        seen.add(marker)
        try:
            for key, item in value.items():
                if not isinstance(key, str):
                    raise TypeError(f"geometry fingerprint mapping keys must be strings at {path}")
                _validate_fingerprint_value(item, path=f"{path}.{key}", seen=seen)
        finally:
            seen.remove(marker)
        return
    if isinstance(value, (list, tuple)):
        marker = id(value)
        if marker in seen:
            raise ValueError(f"cyclic geometry fingerprint sequence at {path}")
        seen.add(marker)
        try:
            for index, item in enumerate(value):
                _validate_fingerprint_value(item, path=f"{path}[{index}]", seen=seen)
        finally:
            seen.remove(marker)
        return
    raise TypeError(
        f"unsupported geometry fingerprint value at {path}: {type(value).__name__}"
    )


def geometry_input_payload(component: Component, inputs: Any = None, *, contract_version: str = GEOMETRY_FINGERPRINT_CONTRACT_VERSION) -> dict[str, Any]:
    """Return the complete versioned local geometry-input identity payload.

    ``component.id`` is intentionally absent because the cache key carries the target
    component id separately.  Appearance/visual data and the world/local transform
    are also intentionally absent: geometry generators must project any geometry-relevant
    request derived from those domains into their explicit ``inputs``/``cache_inputs``.
    """
    payload = {
        "contract_version": contract_version,
        "algorithm": GEOMETRY_FINGERPRINT_ALGORITHM,
        "component": {
            "kind": component.kind,
            "parameters": component.parameters,
            "anchors": component.anchors,
            "constraints": component.constraints,
            "profiles": component.profiles,
            "state": component.state,
            # Geometry is an explicit Component input.  It must participate in
            # identity or authored geometry could alias a generated result.
            "geometry": component.geometry,
        },
        "inputs": inputs,
    }
    _validate_fingerprint_value(payload)
    return payload


def geometry_input_fingerprint(component: Component, inputs: Any = None, *, contract_version: str = GEOMETRY_FINGERPRINT_CONTRACT_VERSION) -> str:
    """Compute the stable local geometry-input fingerprint.

    The digest is SHA-256 over the versioned canonical payload.  Changing the contract
    version therefore creates a deliberate cache boundary instead of silently reusing
    entries produced under different identity semantics.
    """
    return stable_digest(geometry_input_payload(component, inputs, contract_version=contract_version))


def geometry_dependency_fingerprint(graph: RuntimeGraph, component_id: str, additional_dependency_ids: Iterable[str] = (), *, contract_version: str = GEOMETRY_FINGERPRINT_CONTRACT_VERSION) -> str:
    """Fingerprint geometry-relevant hierarchy and relation dependencies only.

    Visual contracts are intentionally excluded. Relation topology is included so
    adding/removing a relation changes the cache identity; relation effect payloads
    are excluded because they belong to visual resolution. Application-specific
    geometry relation metadata must be supplied through the relation's
    ``metadata["geometry_inputs"]`` field.
    """
    node = graph.get(component_id)
    chain = []
    current = node
    while True:
        chain.append({"id": current.id, "geometry": geometry_input_fingerprint(current.component)})
        if current.parent_id is None:
            break
        current = graph.get(current.parent_id)
    chain.reverse()

    relation_index = build_relation_dependency_index(graph)
    dependency_ids = set(relation_index.relation_dependency_nodes(graph, component_id))
    additional = set(additional_dependency_ids)
    unknown = additional - set(graph.nodes)
    if unknown:
        raise KeyError(f"geometry dependency references unknown component(s): {sorted(unknown)}")
    dependency_ids.update(additional)
    relevant_nodes = dependency_ids | {component_id} | {item["id"] for item in chain}

    relation_edges = []
    for relation in graph.relations:
        if relation.source_id not in relevant_nodes and relation.target_id not in relevant_nodes:
            continue
        geometry_inputs = relation.metadata.get("geometry_inputs")
        topology_id = stable_digest({
            "source": relation.source_id,
            "target": relation.target_id,
            "type": relation.relation_type,
            "direction": relation_direction(relation),
            "geometry_inputs": geometry_inputs,
        })
        relation_edges.append({
            "relation_id": topology_id,
            "source": relation.source_id,
            "target": relation.target_id,
            "type": relation.relation_type,
            "direction": relation_direction(relation),
            "geometry_inputs": geometry_inputs,
        })
    relation_edges.sort(key=lambda item: item["relation_id"])
    relation_nodes = [
        {"id": dependency_id, "geometry": geometry_input_fingerprint(graph.get(dependency_id).component)}
        for dependency_id in sorted(dependency_ids)
    ]
    payload = {
        "contract_version": contract_version,
        "algorithm": GEOMETRY_FINGERPRINT_ALGORITHM,
        "hierarchy": chain,
        "relations": relation_edges,
        "relation_nodes": relation_nodes,
    }
    _validate_fingerprint_value(payload)
    return stable_digest(payload)

def geometry_dependency_ids(graph: RuntimeGraph, component_id: str, additional_dependency_ids: Iterable[str] = ()) -> tuple[str, ...]:
    node = graph.get(component_id)
    ids: set[str] = {component_id}
    current = node
    while current.parent_id is not None:
        ids.add(current.parent_id)
        current = graph.get(current.parent_id)
    relation_index = build_relation_dependency_index(graph)
    ids.update(relation_index.relation_dependency_nodes(graph, component_id))
    additional = set(additional_dependency_ids)
    unknown = additional - set(graph.nodes)
    if unknown:
        raise KeyError(f"geometry dependency references unknown component(s): {sorted(unknown)}")
    ids.update(additional)
    return tuple(sorted(ids))

