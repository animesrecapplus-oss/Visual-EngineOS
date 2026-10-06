from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from visual_engine.components.common.geometry_contract import GeometryContract
from visual_engine.runtime.geometry_cache import GeometryCache, GeometryCacheKey
from visual_engine.runtime.generators import GeometryGeneratorRegistry
from visual_engine.runtime.graph import RuntimeGraph
from visual_engine.runtime.versioning import VersionStamp


@dataclass(frozen=True, slots=True)
class GeometryGenerationResult:
    geometry: GeometryContract
    key: GeometryCacheKey
    cache_hit: bool


class CachedGeometryGenerator:
    """Production entry point: registry selection + cache identity + generation."""

    def __init__(self, registry: GeometryGeneratorRegistry, cache: GeometryCache) -> None:
        self.registry = registry
        self.cache = cache

    def generate(
        self,
        graph: RuntimeGraph,
        component_id: str,
        *,
        inputs: Any = None,
        generator: str | None = None,
        version: VersionStamp | None = None,
    ) -> GeometryGenerationResult:
        return self._generate(graph, component_id, inputs=inputs, generator=generator, version=version, stack=())

    def _generate(
        self,
        graph: RuntimeGraph,
        component_id: str,
        *,
        inputs: Any = None,
        generator: str | None = None,
        version: VersionStamp | None = None,
        stack: tuple[str, ...],
    ) -> GeometryGenerationResult:
        if component_id in stack:
            cycle = " -> ".join((*stack, component_id))
            raise ValueError(f"geometry generation dependency cycle: {cycle}")
        component = graph.get(component_id).component
        selected = self.registry.get(generator) if generator is not None else self.registry.for_component(component)
        if not selected.supports(component):
            raise ValueError(f"generator {selected.name!r} does not support component kind {component.kind!r}")

        effective_inputs = selected.default_inputs(component) if inputs is None else inputs
        dependency_ids = selected.geometry_dependencies(component, effective_inputs)
        if component_id in dependency_ids:
            raise ValueError(f"geometry generator {selected.name!r} cannot depend on itself")
        child_geometries: dict[str, GeometryContract] = {}
        for dependency_id in dependency_ids:
            # A declared geometry dependency is an executable dependency, regardless of
            # whether it is a direct child or a cross-branch relation target. This keeps
            # generator semantics honest: if a generator needs another geometry, the
            # orchestration layer must actually resolve it before the generator runs.
            result = self._generate(
                graph, dependency_id, inputs=None, generator=None, version=version,
                stack=(*stack, component_id),
            )
            child_geometries[dependency_id] = result.geometry

        prepared = selected.prepare_inputs(component, effective_inputs, child_geometries)
        cache_inputs = selected.cache_inputs(prepared)
        key = self.cache.make_key(
            graph, component_id,
            generator=selected.name,
            generator_version=selected.version,
            inputs=cache_inputs,
            version=version,
            additional_dependency_ids=dependency_ids,
        )
        geometry, cache_hit = self.cache.get_or_build_with_status(
            key,
            lambda: selected.generate(component, prepared),
            dependency_ids=self.cache_dependency_ids(graph, component_id, dependency_ids),
        )
        return GeometryGenerationResult(geometry, key, cache_hit)

    @staticmethod
    def cache_dependency_ids(graph: RuntimeGraph, component_id: str, additional_dependency_ids: tuple[str, ...] = ()) -> tuple[str, ...]:
        from visual_engine.runtime.geometry_cache import geometry_dependency_ids
        return geometry_dependency_ids(graph, component_id, additional_dependency_ids)
