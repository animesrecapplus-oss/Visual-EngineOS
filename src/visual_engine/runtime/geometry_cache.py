"""Thread-safe geometry cache facade.

Fingerprint construction is isolated in ``geometry_fingerprint`` so cache
concurrency/eviction policy can evolve independently from identity semantics.
"""

from collections import OrderedDict
from dataclasses import dataclass
from threading import Event, RLock
from typing import Any, Callable, Iterable
import json

from visual_engine.components.common.meta import Component
from visual_engine.components.common.geometry_contract import GeometryContract, canonical_geometry_payload, geometry_hash
from visual_engine.runtime.versioning import VersionStamp
from visual_engine.runtime.graph import RuntimeGraph
from .geometry_fingerprint import (GEOMETRY_FINGERPRINT_ALGORITHM, GEOMETRY_FINGERPRINT_CONTRACT_VERSION, GeometryCacheKey, GeometryCacheEntry, GeometryCacheStats, _Inflight, geometry_input_payload as _geometry_input_payload, geometry_input_fingerprint as _geometry_input_fingerprint, geometry_dependency_fingerprint as _geometry_dependency_fingerprint, geometry_dependency_ids)


def geometry_input_payload(component: Component, inputs: Any = None) -> dict[str, Any]:
    # Compatibility wrapper: historical callers could patch the public contract
    # version on this module. Keep that seam while implementation lives elsewhere.
    return _geometry_input_payload(component, inputs, contract_version=GEOMETRY_FINGERPRINT_CONTRACT_VERSION)


def geometry_input_fingerprint(component: Component, inputs: Any = None) -> str:
    return _geometry_input_fingerprint(component, inputs, contract_version=GEOMETRY_FINGERPRINT_CONTRACT_VERSION)


def geometry_dependency_fingerprint(graph: RuntimeGraph, component_id: str, additional_dependency_ids: Iterable[str] = ()) -> str:
    return _geometry_dependency_fingerprint(graph, component_id, additional_dependency_ids, contract_version=GEOMETRY_FINGERPRINT_CONTRACT_VERSION)

class GeometryCache:
    """Thread-safe bounded LRU cache for renderer-neutral geometry contracts."""
    def __init__(self, *, max_entries: int | None = 4096, max_bytes: int | None = 128 * 1024 * 1024) -> None:
        if max_entries is None and max_bytes is None:
            raise ValueError("at least one cache bound must be enabled")
        if max_entries is not None and max_entries <= 0:
            raise ValueError("max_entries must be > 0")
        if max_bytes is not None and max_bytes <= 0:
            raise ValueError("max_bytes must be > 0")
        self.max_entries = max_entries
        self.max_bytes = max_bytes
        self._entries: OrderedDict[GeometryCacheKey, GeometryCacheEntry] = OrderedDict()
        self._reverse_dependencies: dict[str, set[GeometryCacheKey]] = {}
        self._inflight: dict[GeometryCacheKey, _Inflight] = {}
        self._lock = RLock()
        self._hits = self._misses = self._builds = self._evictions = self._invalidations = self._bytes = 0

    @staticmethod
    def _entry_size(geometry: GeometryContract) -> int:
        encoded = json.dumps(canonical_geometry_payload(geometry), sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
        return len(encoded)

    def _attach(self, entry: GeometryCacheEntry) -> None:
        for dependency_id in entry.dependency_ids:
            self._reverse_dependencies.setdefault(dependency_id, set()).add(entry.key)

    def _detach(self, entry: GeometryCacheEntry) -> None:
        for dependency_id in entry.dependency_ids:
            keys = self._reverse_dependencies.get(dependency_id)
            if keys is not None:
                keys.discard(entry.key)
                if not keys:
                    del self._reverse_dependencies[dependency_id]

    def _remove_locked(self, key: GeometryCacheKey) -> bool:
        entry = self._entries.pop(key, None)
        if entry is None:
            return False
        self._bytes -= entry.size_bytes
        self._detach(entry)
        return True

    def _evict_locked(self) -> None:
        while ((self.max_entries is not None and len(self._entries) > self.max_entries) or (self.max_bytes is not None and self._bytes > self.max_bytes)):
            _, entry = self._entries.popitem(last=False)
            self._bytes -= entry.size_bytes
            self._detach(entry)
            self._evictions += 1

    def get(self, key: GeometryCacheKey) -> GeometryContract | None:
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                self._misses += 1
                return None
            self._entries.move_to_end(key)
            self._hits += 1
            return entry.geometry

    def put(self, key: GeometryCacheKey, geometry: GeometryContract, *, dependency_ids: Iterable[str] = ()) -> GeometryCacheEntry:
        if not isinstance(geometry, GeometryContract):
            raise TypeError("geometry must be a GeometryContract")
        raw_deps = tuple(dependency_ids)
        if any(not isinstance(dep, str) or not dep for dep in raw_deps):
            raise ValueError("cache dependency ids must be non-empty strings")
        deps = tuple(sorted(set(raw_deps)))
        entry = GeometryCacheEntry(key, geometry, geometry_hash(geometry), deps, self._entry_size(geometry))
        with self._lock:
            old = self._entries.pop(key, None)
            if old is not None:
                self._bytes -= old.size_bytes
                self._detach(old)
            self._entries[key] = entry
            self._bytes += entry.size_bytes
            self._attach(entry)
            self._evict_locked()
        return entry

    def get_or_build_with_status(
        self,
        key: GeometryCacheKey,
        builder: Callable[[], GeometryContract],
        *,
        dependency_ids: Iterable[str] = (),
    ) -> tuple[GeometryContract, bool]:
        """Return ``(geometry, cache_hit)`` without changing the legacy API.

        Waiters on an in-flight build are considered hits from the caller's point
        of view: they did not execute the generator. The owner is the only caller
        counted as a build.
        """
        while True:
            with self._lock:
                entry = self._entries.get(key)
                if entry is not None:
                    self._entries.move_to_end(key)
                    self._hits += 1
                    return entry.geometry, True
                self._misses += 1
                flight = self._inflight.get(key)
                if flight is None:
                    flight = _Inflight(Event())
                    self._inflight[key] = flight
                    owner = True
                else:
                    owner = False
            if owner:
                break
            flight.event.wait()
            if flight.error is not None:
                raise flight.error
            # The completed build may have been evicted immediately because of a
            # very small cache budget. Retry through the normal lookup path.
            with self._lock:
                if key in self._entries:
                    self._hits += 1
                    self._entries.move_to_end(key)
                    return self._entries[key].geometry, True

        try:
            geometry = builder()
            if not isinstance(geometry, GeometryContract):
                raise TypeError("geometry builder must return GeometryContract")
            with self._lock:
                entry = self.put(key, geometry, dependency_ids=dependency_ids)
                self._builds += 1
                self._inflight.pop(key).event.set()
                return entry.geometry, False
        except BaseException as exc:
            with self._lock:
                flight = self._inflight.pop(key)
                flight.error = exc
                flight.event.set()
            raise

    def get_or_build(self, key: GeometryCacheKey, builder: Callable[[], GeometryContract], *, dependency_ids: Iterable[str] = ()) -> GeometryContract:
        geometry, _ = self.get_or_build_with_status(key, builder, dependency_ids=dependency_ids)
        return geometry

    def make_key(self, graph: RuntimeGraph, component_id: str, *, generator: str, generator_version: str, inputs: Any = None, version: VersionStamp | None = None, additional_dependency_ids: Iterable[str] = ()) -> GeometryCacheKey:
        if not generator or not generator_version:
            raise ValueError("generator and generator_version must be non-empty")
        version = version or VersionStamp()
        return GeometryCacheKey(component_id, geometry_dependency_fingerprint(graph, component_id, additional_dependency_ids), geometry_input_fingerprint(graph.get(component_id).component, inputs), generator, generator_version, version)

    def get_or_build_for_graph(self, graph: RuntimeGraph, component_id: str, builder: Callable[[], GeometryContract], *, generator: str, generator_version: str, inputs: Any = None, version: VersionStamp | None = None, additional_dependency_ids: Iterable[str] = ()) -> GeometryContract:
        key = self.make_key(graph, component_id, generator=generator, generator_version=generator_version, inputs=inputs, version=version, additional_dependency_ids=additional_dependency_ids)
        return self.get_or_build(key, builder, dependency_ids=geometry_dependency_ids(graph, component_id, additional_dependency_ids))

    def invalidate(self, key: GeometryCacheKey) -> bool:
        with self._lock:
            removed = self._remove_locked(key)
            if removed:
                self._invalidations += 1
            return removed

    def invalidate_component(self, component_id: str) -> int:
        with self._lock:
            keys = tuple(self._reverse_dependencies.get(component_id, ()))
            removed = sum(1 for key in keys if self._remove_locked(key))
            self._invalidations += removed
            return removed

    def clear(self) -> int:
        with self._lock:
            count = len(self._entries)
            self._entries.clear(); self._reverse_dependencies.clear(); self._bytes = 0
            self._invalidations += count
            return count

    def stats(self) -> GeometryCacheStats:
        with self._lock:
            return GeometryCacheStats(self._hits, self._misses, self._builds, self._evictions, self._invalidations, len(self._entries), self._bytes)

    def keys(self) -> tuple[GeometryCacheKey, ...]:
        with self._lock:
            return tuple(self._entries.keys())
