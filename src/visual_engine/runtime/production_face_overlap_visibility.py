from __future__ import annotations

"""Canonical production resolver for the existing Head→child overlap proof.

The module owns only the production-face overlap contract. Geometry-owner extraction
remains owned by ``production_slice`` and is injected explicitly to avoid duplicating
that responsibility or creating a dependency cycle.
"""

from dataclasses import dataclass
from typing import Callable

from visual_engine.components.common.geometry_contract import GeometryContract
from visual_engine.components.common.meta import Component
from visual_engine.runtime.coverage import DepthRelation, Occluder
from visual_engine.runtime.region_maps import generic_geometry_region_map
from visual_engine.runtime.semantic_regions import RegionMap
from visual_engine.runtime.visibility import VisibilityResult, resolve_visibility
from visual_engine.runtime.visibility_attribution import (
    VisibilityAttributionResult,
    resolve_visibility_attribution,
)

OwnerGeometryResolver = Callable[[GeometryContract, str], tuple[GeometryContract, float]]


@dataclass(frozen=True, slots=True)
class ProductionVisibilityResolution:
    """Immutable proof returned for one production Head→child overlap request."""

    target_id: str
    occluder_id: str
    target_depth: float
    occluder_depth: float
    target_regions: RegionMap
    occluder_regions: RegionMap
    visibility: VisibilityResult
    attribution: VisibilityAttributionResult
    occluder_ids: tuple[str, ...] = ()
    occluder_depths: tuple[float, ...] = ()

    def __post_init__(self) -> None:
        ids = self.occluder_ids or (self.occluder_id,)
        depths = self.occluder_depths or (self.occluder_depth,)
        if len(ids) != len(depths) or not ids or len(set(ids)) != len(ids):
            raise ValueError("production visibility occluder ids/depths must be aligned and unique")
        if self.target_id in ids:
            raise ValueError("production visibility target cannot be its occluder")
        object.__setattr__(self, "occluder_ids", tuple(ids))
        object.__setattr__(self, "occluder_depths", tuple(float(v) for v in depths))

    @property
    def depth_relation(self) -> DepthRelation:
        return self.visibility.regions[0].depth_relation if self.visibility.regions else DepthRelation.UNKNOWN

    @property
    def blocked_area(self) -> float:
        return sum(region.blocked_area for region in self.visibility.regions)

    @property
    def visible_area(self) -> float:
        return sum(region.area * region.visible for region in self.visibility.regions)


def resolve_face_overlap_visibility(
    root: Component,
    camera_geometry: GeometryContract,
    occluder_ids: tuple[str, ...],
    *,
    owner_geometry: OwnerGeometryResolver,
) -> ProductionVisibilityResolution:
    """Resolve the certified Head→Nose/Mouth production overlap without inference."""
    if not isinstance(root, Component):
        raise TypeError("production visibility root must be a Component")
    if not isinstance(camera_geometry, GeometryContract):
        raise TypeError("production visibility camera_geometry must be a GeometryContract")
    if not callable(owner_geometry):
        raise TypeError("production visibility owner_geometry must be callable")
    if (not occluder_ids or any(not isinstance(owner_id, str) or not owner_id for owner_id in occluder_ids)
            or len(set(occluder_ids)) != len(occluder_ids)):
        raise ValueError("production visibility requires unique occluder ids")
    head_geometry, head_depth = owner_geometry(camera_geometry, root.id)
    target_regions = generic_geometry_region_map(root, head_geometry)
    if not target_regions.regions:
        raise ValueError("production visibility head target produced no semantic area regions")
    occluders: list[Occluder] = []
    depths: list[float] = []
    first_regions: RegionMap | None = None
    for owner_id in occluder_ids:
        child = root.find(owner_id)
        if child is None:
            raise ValueError(f"production visibility requires component {owner_id!r}")
        child_geometry, child_depth = owner_geometry(camera_geometry, child.id)
        child_regions = generic_geometry_region_map(child, child_geometry)
        if len(child_regions.regions) != 1:
            raise ValueError(f"production visibility occluder {owner_id!r} must resolve to exactly one area region")
        if first_regions is None:
            first_regions = child_regions
        occluders.append(Occluder(child.id, child_regions.regions[0].geometry, z=child_depth))
        depths.append(child_depth)
    visibility = resolve_visibility(root.id, target_regions, tuple(occluders), target_z=head_depth)
    attribution = resolve_visibility_attribution(root.id, target_regions, tuple(occluders), target_z=head_depth)
    first = occluders[0]
    assert first_regions is not None
    return ProductionVisibilityResolution(
        target_id=root.id, occluder_id=first.occluder_id,
        target_depth=head_depth, occluder_depth=first.z,
        target_regions=target_regions, occluder_regions=first_regions,
        visibility=visibility, attribution=attribution,
        occluder_ids=tuple(occluder_ids), occluder_depths=tuple(depths),
    )
