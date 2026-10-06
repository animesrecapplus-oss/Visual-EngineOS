from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Any

from visual_engine.components.common.geometry_contract import GeometryBounds, GeometryContract, GeometryPrimitive
from visual_engine.components.common.meta import Component
from visual_engine.runtime.geometry_transform import resolve_geometry_contract
from visual_engine.runtime.graph import RuntimeGraph
from visual_engine.runtime.semantic_regions import RegionMap, SemanticRegion
from visual_engine.runtime.region_geometry import path_to_region, region_to_contract
from visual_engine.scene.composition import Camera, Placement


class SemanticRegionProvider(Protocol):
    """Build semantic regions in the component's local coordinate frame."""
    name: str
    version: str
    def supports(self, component: Component) -> bool: ...
    def build(self, component: Component, geometry: GeometryContract) -> RegionMap: ...


@dataclass(frozen=True, slots=True)
class RegisteredSemanticRegionProvider:
    name: str
    version: str
    kinds: tuple[str, ...]
    build_fn: Any

    def supports(self, component: Component) -> bool:
        return component.kind in self.kinds

    def build(self, component: Component, geometry: GeometryContract) -> RegionMap:
        region_map = self.build_fn(component, geometry)
        if region_map.target_id != component.id:
            raise ValueError("region provider returned a RegionMap for another component")
        return region_map


@dataclass(slots=True)
class SemanticRegionProviderRegistry:
    _providers: list[RegisteredSemanticRegionProvider]

    def __init__(self) -> None:
        self._providers = []

    def register(self, provider: RegisteredSemanticRegionProvider, *, default: bool = True) -> None:
        if any(p.name == provider.name for p in self._providers):
            raise ValueError(f"Duplicate semantic region provider: {provider.name}")
        if not provider.name or not provider.version:
            raise ValueError("Semantic region provider name/version are required")
        self._providers.append(provider)
        if default:
            self._providers.sort(key=lambda p: p.name)

    def get(self, name: str) -> RegisteredSemanticRegionProvider:
        for provider in self._providers:
            if provider.name == name:
                return provider
        raise KeyError(name)

    def for_component(self, component: Component) -> RegisteredSemanticRegionProvider:
        matches = [p for p in self._providers if p.supports(component)]
        if not matches:
            raise KeyError(f"No semantic region provider for component kind {component.kind!r}")
        return matches[0]


@dataclass(frozen=True, slots=True)
class RegionMapResolution:
    """A component's semantic regions resolved into one explicit spatial frame."""
    component_id: str
    provider: str
    provider_version: str
    coordinate_frame: str
    region_map: RegionMap

    def __post_init__(self) -> None:
        if not self.component_id or not self.provider or not self.provider_version:
            raise ValueError("RegionMapResolution identity is required")
        if self.region_map.target_id != self.component_id:
            raise ValueError("resolved RegionMap target does not match component")
        if not self.coordinate_frame:
            raise ValueError("coordinate_frame is required")


def _primitive_bounds(primitive: GeometryPrimitive) -> GeometryBounds:
    data = dict(primitive.data)
    if primitive.kind == "polygon":
        points = tuple(data.get("points", ()))
        if len(points) < 3:
            return GeometryBounds()
        xs = [float(p[0]) for p in points]
        ys = [float(p[1]) for p in points]
        return GeometryBounds(min(xs), min(ys), max(xs), max(ys))
    if primitive.kind in {"ellipse", "circle"} and "cx" in data and "cy" in data:
        rx = ry = float(data.get("r", 0.0))
        if "r" not in data:
            rx, ry = float(data.get("rx", 0.0)), float(data.get("ry", 0.0))
        return GeometryBounds(float(data["cx"]) - rx, float(data["cy"]) - ry, float(data["cx"]) + rx, float(data["cy"]) + ry)
    return GeometryBounds()


def _primitive_region_id(component_id: str, index: int, primitive_kind: str, data: dict) -> str:
    role = data.get("semantic_region", data.get("role"))
    suffix = str(role) if role else f"primitive_{index}_{primitive_kind}"
    if "index" in data:
        suffix = f"{suffix}_{data['index']}"
    return f"{component_id}:region:{suffix}"


def generic_geometry_region_map(component: Component, geometry: GeometryContract) -> RegionMap:
    """Expose explicitly labelled area primitives as semantic regions.

    The provider has no knowledge of eyes, hands, clothing, anatomy, or object types.
    Generators define semantic vocabulary by labelling area primitives.
    """
    regions: list[SemanticRegion] = []
    for index, primitive in enumerate(geometry.primitives):
        if primitive.kind not in {"polygon", "ellipse", "circle"}:
            continue
        data = dict(primitive.data)
        name = str(data.get("semantic_region", data.get("role", primitive.kind)))
        region_id = _primitive_region_id(component.id, index, primitive.kind, data)
        region_geometry = GeometryContract(
            coordinate_frame=geometry.coordinate_frame,
            bounds=_primitive_bounds(primitive),
            primitives=(primitive,),
            local_z=geometry.local_z,
        )
        regions.append(SemanticRegion(region_id=region_id, name=name, geometry=region_geometry))

    # Production HumanFace head/nose surfaces are closed Bézier paths rather than
    # area primitives. Only explicitly surfaced closed paths become semantic regions;
    # open detail strokes (for example nostrils) therefore remain non-area geometry.
    for surface in geometry.surfaces:
        raw_index = surface.data.get("path_index")
        if raw_index is None:
            continue
        index = int(raw_index)
        if index < 0 or index >= len(geometry.paths):
            raise ValueError(f"surface {surface.name!r} references an invalid path index")
        path = geometry.paths[index]
        if not path.commands or path.commands[-1][0] != "Z":
            continue
        region = path_to_region(path)
        if region.is_empty or region.area <= 1e-9:
            raise ValueError(f"surface {surface.name!r} closed path has no positive area")
        name = str(surface.data.get("semantic_region", surface.name.rsplit(":", 1)[-1]))
        owner = str(surface.data.get("source_component_id", component.id))
        # Convert the validated closed path once into area primitives. The generic
        # visibility kernel remains primitive-only, so ordinary renderer paths never
        # become accidental occluders. Holes are rejected here rather than dropped.
        contract_region = region_to_contract(region, coordinate_frame=geometry.coordinate_frame)
        if any(polygon.holes for polygon in contract_region.polygons):
            raise ValueError(f"surface {surface.name!r} closed path contains holes not representable by generic region primitives")
        primitives = tuple(
            GeometryPrimitive("polygon", {"points": polygon.exterior, "semantic_region": name})
            for polygon in contract_region.polygons
        )
        min_x, min_y, max_x, max_y = region.bounds
        region_geometry = GeometryContract(
            coordinate_frame=geometry.coordinate_frame,
            bounds=GeometryBounds(min_x, min_y, max_x, max_y),
            primitives=primitives,
            surfaces=(surface,),
            local_z=geometry.local_z,
        )
        regions.append(SemanticRegion(
            region_id=f"{owner}:region:path:{index}:{name}",
            name=name,
            geometry=region_geometry,
            metadata={"owner": owner, "path_index": str(index)},
        ))
    return RegionMap(component.id, tuple(regions))


def generic_region_provider(*, kinds: tuple[str, ...]) -> RegisteredSemanticRegionProvider:
    return RegisteredSemanticRegionProvider("generic.geometry_primitives", "1", kinds, generic_geometry_region_map)


def resolve_region_map(
    graph: RuntimeGraph,
    component_id: str,
    geometry: GeometryContract,
    registry: SemanticRegionProviderRegistry,
    *,
    placement: Placement | None = None,
    camera: Camera | None = None,
    target: str = "world",
    provider: str | None = None,
) -> RegionMapResolution:
    """Build local semantic regions and resolve every region through the spatial pipeline."""
    component = graph.get(component_id).component
    selected = registry.get(provider) if provider is not None else registry.for_component(component)
    if not selected.supports(component):
        raise ValueError(f"region provider {selected.name!r} does not support {component.kind!r}")
    local_map = selected.build(component, geometry)
    if target not in {"local", "world", "scene", "camera"}:
        raise ValueError("target must be local, world, scene or camera")
    if target == "local":
        resolved = local_map
    else:
        resolved = RegionMap(component_id, tuple(
            SemanticRegion(
                region_id=r.region_id, name=r.name,
                geometry=resolve_geometry_contract(graph, component_id, r.geometry, placement=placement, camera=camera, target=target),
                kind=r.kind, parent_region_id=r.parent_region_id, tags=r.tags, metadata=r.metadata,
            ) for r in local_map.regions
        ))
    return RegionMapResolution(component_id, selected.name, selected.version, target, resolved)
