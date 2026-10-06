from __future__ import annotations

"""Production adapter for the measured HumanFace-head → Ear relation."""

from dataclasses import dataclass

from visual_engine.components.common.geometry_contract import GeometryContract
from visual_engine.components.common.meta import Component
from visual_engine.runtime.coverage import DepthRelation
from visual_engine.runtime.production_pair_occlusion import ProductionPairOcclusion, resolve_production_pair_occlusion
from visual_engine.runtime.semantic_regions import RegionMap
from visual_engine.runtime.visibility import VisibilityResult
from visual_engine.runtime.visibility_attribution import VisibilityAttributionResult


@dataclass(frozen=True, slots=True)
class ProductionHeadEarOcclusion:
    """Immutable evidence for one Ear target covered by the HumanFace head surface."""

    ear_id: str
    head_id: str
    ear_depth: float
    head_depth: float
    ear_regions: RegionMap
    head_regions: RegionMap
    visibility: VisibilityResult
    attribution: VisibilityAttributionResult | None

    @classmethod
    def from_pair(cls, pair: ProductionPairOcclusion) -> "ProductionHeadEarOcclusion":
        return cls(
            pair.target_id, pair.occluder_id, pair.target_depth, pair.occluder_depth,
            pair.target_regions, pair.occluder_regions, pair.visibility, pair.attribution,
        )

    def __post_init__(self) -> None:
        if not self.ear_id or not self.head_id or self.ear_id == self.head_id:
            raise ValueError("Head/Ear occlusion requires distinct non-empty owner ids")
        if self.ear_regions.target_id != self.ear_id or self.head_regions.target_id != self.head_id:
            raise ValueError("Head/Ear region maps must preserve their owner ids")
        if self.visibility.target_id != self.ear_id:
            raise ValueError("Head/Ear visibility evidence must target the Ear")
        if self.attribution is not None:
            raise ValueError("Head/Ear production relation does not claim causal attribution")

    @property
    def coverage(self) -> float:
        return self.visibility.overall_coverage

    @property
    def visible(self) -> float:
        return self.visibility.overall_visible

    @property
    def depth_relation(self) -> DepthRelation:
        return self.visibility.regions[0].depth_relation if self.visibility.regions else DepthRelation.UNKNOWN


def resolve_head_ear_occlusion(
    ear: Component,
    ear_geometry: GeometryContract,
    ear_depth: float,
    head_owner: Component,
    head_geometry: GeometryContract,
    head_depth: float,
    *,
    head_opacity: float = 1.0,
    head_transmission: float = 0.0,
) -> ProductionHeadEarOcclusion:
    """Resolve head-over-ear paint order as explicit coplanar semantic occlusion."""
    if ear.kind != "Ear" or head_owner.kind != "HumanFace":
        raise ValueError("Head/Ear production adapter requires Ear then HumanFace components")
    pair = resolve_production_pair_occlusion(
        ear, ear_geometry, ear_depth, head_owner, head_geometry, head_depth,
        occluder_opacity=head_opacity, occluder_transmission=head_transmission,
        coplanar_occludes=True, include_attribution=False,
    )
    return ProductionHeadEarOcclusion.from_pair(pair)
