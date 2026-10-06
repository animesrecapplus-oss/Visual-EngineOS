from __future__ import annotations

"""Close the generic placement -> region -> visibility pipeline.

This module is deliberately domain-neutral.  It does not know whether a source is
an eye, hand, garment, tool, animal, building, or any other entity.  A placement
solution is materialized into a common frame, the source's semantic regions are
materialized with the same transform, and the resulting source geometry is passed
to the existing visibility kernel.
"""

from dataclasses import dataclass
from typing import Iterable

from visual_engine.components.common.geometry_contract import GeometryContract
from visual_engine.components.common.meta import Component
from visual_engine.runtime.geometry_contract_transform import transform_geometry_contract
from visual_engine.runtime.semantic_regions import RegionMap, SemanticRegion
from visual_engine.runtime.region_maps import (
    SemanticRegionProviderRegistry,
    generic_geometry_region_map,
)
from visual_engine.runtime.placement import PlacementSolution
from visual_engine.runtime.visibility import (
    AffectedRegionEvent,
    Occluder,
    VisibilityResult,
    resolve_visibility,
)


@dataclass(frozen=True, slots=True)
class PlacementVisibilityResolution:
    """Complete spatial/visibility result for one placed source object."""

    source_id: str
    target_id: str
    coordinate_frame: str
    source_geometry: GeometryContract
    source_regions: RegionMap
    visibility: VisibilityResult

    @property
    def events(self) -> tuple[AffectedRegionEvent, ...]:
        return self.visibility.events

    def __post_init__(self) -> None:
        if not self.source_id or not self.target_id:
            raise ValueError("placement visibility identity is required")
        if self.source_geometry.coordinate_frame != self.coordinate_frame:
            raise ValueError("source geometry frame does not match resolution frame")
        if self.source_regions.target_id != self.source_id:
            raise ValueError("source RegionMap target does not match source")
        if self.visibility.target_id != self.target_id:
            raise ValueError("visibility target does not match resolution target")


def materialize_region_map(
    region_map: RegionMap,
    matrix: tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]],
    *,
    coordinate_frame: str,
    z_offset: float = 0.0,
) -> RegionMap:
    """Apply exactly the placement transform to every semantic source region."""
    return RegionMap(
        region_map.target_id,
        tuple(
            SemanticRegion(
                region_id=region.region_id,
                name=region.name,
                geometry=transform_geometry_contract(
                    region.geometry,
                    matrix,
                    z_offset=z_offset,
                    coordinate_frame=coordinate_frame,
                ),
                kind=region.kind,
                parent_region_id=region.parent_region_id,
                tags=region.tags,
                metadata=region.metadata,
            )
            for region in region_map.regions
        ),
    )


def resolve_placement_visibility(
    source_component: Component,
    source_geometry: GeometryContract,
    placement: PlacementSolution,
    target_regions: RegionMap,
    *,
    region_registry: SemanticRegionProviderRegistry | None = None,
    region_provider: str | None = None,
    coordinate_frame: str | None = None,
    target_z: float = 0.0,
    opacity: float = 1.0,
    transmission: float = 0.0,
    coplanar_occludes: bool = False,
    ellipse_segments: int = 128,
) -> PlacementVisibilityResolution:
    """Materialize one placement and immediately resolve its target impact.

    Preconditions are explicit: ``source_geometry`` and ``target_regions`` must
    describe compatible 2D frames before the placement is applied.  The placement
    matrix is the sole source transform here; no object-specific placement is
    inferred.

    A registered semantic-region provider is used when supplied.  Without one,
    the generic provider exposes labelled area primitives as source regions.  The
    visibility kernel itself only consumes the resulting geometry and target
    regions, so source/target object categories never enter the algorithm.
    """
    if placement.source_id != source_component.id:
        raise ValueError("placement source_id does not match source component")
    if placement.target_id != target_regions.target_id:
        raise ValueError("placement target_id does not match target RegionMap")
    if not source_geometry.coordinate_frame:
        raise ValueError("source geometry coordinate frame is required")
    target_frames = {r.geometry.coordinate_frame for r in target_regions.regions}
    if target_frames and len(target_frames) != 1:
        raise ValueError("target RegionMap must use one coordinate frame")
    target_frame = next(iter(target_frames), coordinate_frame or "scene")
    frame = coordinate_frame or target_frame
    if target_frames and frame != target_frame:
        raise ValueError("coordinate frame does not match target RegionMap")

    # Build semantic regions in source-local space before applying the placement.
    registry = region_registry
    if registry is None:
        local_regions = generic_geometry_region_map(source_component, source_geometry)
    else:
        provider = registry.get(region_provider) if region_provider is not None else registry.for_component(source_component)
        if not provider.supports(source_component):
            raise ValueError(f"region provider {provider.name!r} does not support {source_component.kind!r}")
        local_regions = provider.build(source_component, source_geometry)

    # The placement solution already contains the resolved local->target-frame
    # affine transform.  Do not run component/world transforms a second time.
    placed_geometry = transform_geometry_contract(
        source_geometry,
        placement.matrix,
        z_offset=placement.z_offset,
        coordinate_frame=frame,
    )
    placed_regions = materialize_region_map(
        local_regions,
        placement.matrix,
        z_offset=placement.z_offset,
        coordinate_frame=frame,
    )

    occluder_z = float(target_z + source_geometry.local_z + placement.z_offset)
    occluder = Occluder(
        occluder_id=source_component.id,
        geometry=placed_geometry,
        z=occluder_z,
        opacity=opacity,
        transmission=transmission,
    )
    visibility = resolve_visibility(
        target_regions.target_id,
        target_regions,
        (occluder,),
        target_z=target_z,
        coplanar_occludes=coplanar_occludes,
        ellipse_segments=ellipse_segments,
    )
    return PlacementVisibilityResolution(
        source_id=source_component.id,
        target_id=target_regions.target_id,
        coordinate_frame=frame,
        source_geometry=placed_geometry,
        source_regions=placed_regions,
        visibility=visibility,
    )
