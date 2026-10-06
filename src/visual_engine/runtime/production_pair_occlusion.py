from __future__ import annotations

"""Domain-neutral production adapter for one owner-pair occlusion relation."""

from dataclasses import dataclass
import math

from visual_engine.components.common.geometry_contract import GeometryContract
from visual_engine.components.common.meta import Component
from visual_engine.runtime.coverage import DepthRelation, Occluder
from visual_engine.runtime.region_maps import generic_geometry_region_map
from visual_engine.runtime.semantic_regions import RegionMap
from visual_engine.runtime.visibility import VisibilityResult, resolve_visibility
from visual_engine.runtime.visibility_attribution import VisibilityAttributionResult, resolve_visibility_attribution


@dataclass(frozen=True, slots=True)
class ProductionPairOcclusion:
    """Immutable visibility/attribution evidence for one target/occluder pair."""

    target_id: str
    occluder_id: str
    target_depth: float
    occluder_depth: float
    target_regions: RegionMap
    occluder_regions: RegionMap
    visibility: VisibilityResult
    attribution: VisibilityAttributionResult | None

    def __post_init__(self) -> None:
        if not self.target_id or not self.occluder_id or self.target_id == self.occluder_id:
            raise ValueError("production pair occlusion requires distinct non-empty owner ids")
        if self.target_regions.target_id != self.target_id or self.occluder_regions.target_id != self.occluder_id:
            raise ValueError("production pair region maps must preserve owner ids")
        if self.visibility.target_id != self.target_id:
            raise ValueError("production pair visibility evidence must target the declared owner")
        if self.attribution is not None and self.attribution.target_id != self.target_id:
            raise ValueError("production pair attribution evidence must target the declared owner")

    @property
    def coverage(self) -> float:
        return self.visibility.overall_coverage

    @property
    def visible(self) -> float:
        return self.visibility.overall_visible

    @property
    def depth_relation(self) -> DepthRelation:
        return self.visibility.regions[0].depth_relation if self.visibility.regions else DepthRelation.UNKNOWN


def resolve_production_pair_occlusion(
    target: Component,
    target_geometry: GeometryContract,
    target_depth: float,
    occluder: Component,
    occluder_geometry: GeometryContract,
    occluder_depth: float,
    *,
    occluder_opacity: float = 1.0,
    occluder_transmission: float = 0.0,
    coplanar_occludes: bool = False,
    include_attribution: bool = True,
) -> ProductionPairOcclusion:
    """Resolve one real owner pair through the authoritative generic kernels."""
    if target.id == occluder.id:
        raise ValueError("production pair occlusion owners must be distinct")
    if not isinstance(coplanar_occludes, bool):
        raise TypeError("coplanar_occludes must be bool")
    if not isinstance(include_attribution, bool):
        raise TypeError("include_attribution must be bool")
    values = (
        ("target_depth", target_depth), ("occluder_depth", occluder_depth),
        ("occluder_opacity", occluder_opacity), ("occluder_transmission", occluder_transmission),
    )
    for name, value in values:
        if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
            raise ValueError(f"{name} must be finite")
    if not 0.0 <= float(occluder_opacity) <= 1.0 or not 0.0 <= float(occluder_transmission) <= 1.0:
        raise ValueError("occluder opacity/transmission must be in [0,1]")

    target_regions = generic_geometry_region_map(target, target_geometry)
    occluder_regions = generic_geometry_region_map(occluder, occluder_geometry)
    if len(target_regions.regions) != 1 or len(occluder_regions.regions) != 1:
        raise ValueError("production pair occlusion requires exactly one area region per owner")
    spatial = Occluder(
        occluder.id,
        occluder_regions.regions[0].geometry,
        z=float(occluder_depth),
        opacity=float(occluder_opacity),
        transmission=float(occluder_transmission),
    )
    visibility = resolve_visibility(
        target.id, target_regions, (spatial,), target_z=float(target_depth),
        coplanar_occludes=coplanar_occludes,
    )
    attribution = None
    if include_attribution:
        attribution = resolve_visibility_attribution(
            target.id, target_regions, (spatial,), target_z=float(target_depth),
            coplanar_occludes=coplanar_occludes,
        )
    return ProductionPairOcclusion(
        target.id, occluder.id, float(target_depth), float(occluder_depth),
        target_regions, occluder_regions, visibility, attribution,
    )
