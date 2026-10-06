from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Protocol

from visual_engine.components.common.geometry_contract import GeometryContract
from visual_engine.components.common.meta import Component


class GeometryGenerator(Protocol):
    """Contract implemented by every deterministic geometry generator."""

    name: str
    version: str

    def supports(self, component: Component) -> bool: ...

    def default_inputs(self, component: Component) -> Any: ...

    def cache_inputs(self, inputs: Any = None) -> Any: ...

    def geometry_dependencies(self, component: Component, inputs: Any = None) -> tuple[str, ...]: ...

    def prepare_inputs(self, component: Component, inputs: Any, child_geometries: Mapping[str, GeometryContract]) -> Any: ...

    def generate(self, component: Component, inputs: Any = None) -> GeometryContract: ...


@dataclass(frozen=True, slots=True)
class RegisteredGeometryGenerator:
    name: str
    version: str
    kinds: tuple[str, ...]
    generate_fn: Callable[[Component, Any], GeometryContract]
    cache_inputs_fn: Callable[[Any], Any] = lambda inputs: inputs
    default_inputs_fn: Callable[[Component], Any] = lambda component: None
    geometry_dependencies_fn: Callable[[Component, Any], tuple[str, ...]] = lambda component, inputs: ()
    prepare_inputs_fn: Callable[[Component, Any, Mapping[str, GeometryContract]], Any] = lambda component, inputs, children: inputs

    def __post_init__(self) -> None:
        if not self.name or not self.version:
            raise ValueError("geometry generator name/version must be non-empty")
        if not self.kinds or any(not kind for kind in self.kinds):
            raise ValueError("geometry generator must support at least one component kind")
        if any(not isinstance(kind, str) or not kind for kind in self.kinds):
            raise ValueError("geometry generator kinds must be non-empty strings")

    def supports(self, component: Component) -> bool:
        return component.kind in self.kinds

    def default_inputs(self, component: Component) -> Any:
        return self.default_inputs_fn(component)

    def cache_inputs(self, inputs: Any = None) -> Any:
        return self.cache_inputs_fn(inputs)

    def geometry_dependencies(self, component: Component, inputs: Any = None) -> tuple[str, ...]:
        values = tuple(self.geometry_dependencies_fn(component, inputs))
        if any(not isinstance(value, str) or not value for value in values):
            raise ValueError(f"geometry generator {self.name!r} returned an invalid dependency id")
        return tuple(sorted(set(values)))

    def prepare_inputs(self, component: Component, inputs: Any = None, child_geometries: Mapping[str, GeometryContract] | None = None) -> Any:
        return self.prepare_inputs_fn(component, inputs, child_geometries or {})

    def generate(self, component: Component, inputs: Any = None) -> GeometryContract:
        geometry = self.generate_fn(component, inputs)
        if not isinstance(geometry, GeometryContract):
            raise TypeError(f"geometry generator {self.name!r} must return GeometryContract")
        return geometry


class GeometryGeneratorRegistry:
    """Deterministic registry mapping component kinds to geometry generators."""

    def __init__(self) -> None:
        self._by_name: dict[str, RegisteredGeometryGenerator] = {}
        self._by_kind: dict[str, str] = {}

    def register(self, generator: RegisteredGeometryGenerator, *, replace: bool = False, default: bool = True) -> None:
        if generator.name in self._by_name and not replace:
            raise ValueError(f"geometry generator already registered: {generator.name}")
        if generator.name in self._by_name:
            old = self._by_name[generator.name]
            for kind in old.kinds:
                if self._by_kind.get(kind) == old.name:
                    del self._by_kind[kind]
        if default:
            for kind in generator.kinds:
                existing = self._by_kind.get(kind)
                if existing is not None and existing != generator.name and not replace:
                    raise ValueError(f"a default geometry generator is already registered for kind: {kind}")
        self._by_name[generator.name] = generator
        if default:
            for kind in generator.kinds:
                self._by_kind[kind] = generator.name

    def unregister(self, name: str) -> None:
        generator = self._by_name.pop(name, None)
        if generator is None:
            raise KeyError(name)
        for kind in generator.kinds:
            if self._by_kind.get(kind) == name:
                del self._by_kind[kind]

    def get(self, name: str) -> RegisteredGeometryGenerator:
        try:
            return self._by_name[name]
        except KeyError as exc:
            raise KeyError(f"unknown geometry generator: {name}") from exc

    def for_component(self, component: Component) -> RegisteredGeometryGenerator:
        name = self._by_kind.get(component.kind)
        if name is None:
            raise KeyError(f"no geometry generator registered for component kind: {component.kind}")
        return self._by_name[name]

    def generate(self, component: Component, inputs: Any = None, *, generator: str | None = None) -> GeometryContract:
        selected = self.get(generator) if generator is not None else self.for_component(component)
        if not selected.supports(component):
            raise ValueError(f"generator {selected.name!r} does not support component kind {component.kind!r}")
        return selected.generate(component, inputs)

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._by_name))

    def defaults(self) -> Mapping[str, str]:
        return dict(sorted(self._by_kind.items()))
