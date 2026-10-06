from __future__ import annotations

"""Production adapter for the certified Hair → Ear relation."""

from dataclasses import dataclass

from visual_engine.components.common.geometry_contract import GeometryContract
from visual_engine.components.common.meta import Component
from visual_engine.runtime.coverage import DepthRelation
from visual_engine.runtime.production_pair_occlusion import ProductionPairOcclusion, resolve_production_pair_occlusion
from visual_engine.runtime.semantic_regions import RegionMap
from visual_engine.runtime.visibility import VisibilityResult
from visual_engine.runtime.visibility_attribution import VisibilityAttributionResult


@dataclass(frozen=True, slots=True)
class ProductionHairEarOcclusion:
    """Immutable production evidence for one Ear target occluded by Hair."""

    ear_id: str
    hair_id: str
    ear_depth: float
    hair_depth: float
    ear_regions: RegionMap
    hair_regions: RegionMap
    visibility: VisibilityResult
    attribution: VisibilityAttributionResult

    @classmethod
    def from_pair(cls, pair: ProductionPairOcclusion) -> "ProductionHairEarOcclusion":
        return cls(
            pair.target_id, pair.occluder_id, pair.target_depth, pair.occluder_depth,
            pair.target_regions, pair.occluder_regions, pair.visibility, pair.attribution,
        )

    def __post_init__(self) -> None:
        if not self.ear_id or not self.hair_id or self.ear_id == self.hair_id:
            raise ValueError("Hair/Ear occlusion requires distinct non-empty owner ids")
        if self.ear_regions.target_id != self.ear_id or self.hair_regions.target_id != self.hair_id:
            raise ValueError("Hair/Ear region maps must preserve their owner ids")
        if self.visibility.target_id != self.ear_id or self.attribution is None or self.attribution.target_id != self.ear_id:
            raise ValueError("Hair/Ear visibility and attribution evidence must target the Ear")

    @property
    def coverage(self) -> float:
        return self.visibility.overall_coverage

    @property
    def visible(self) -> float:
        return self.visibility.overall_visible

    @property
    def depth_relation(self) -> DepthRelation:
        return self.visibility.regions[0].depth_relation if self.visibility.regions else DepthRelation.UNKNOWN


def resolve_hair_ear_occlusion(
    ear: Component,
    ear_geometry: GeometryContract,
    ear_depth: float,
    hair: Component,
    hair_geometry: GeometryContract,
    hair_depth: float,
    *,
    hair_opacity: float = 1.0,
    hair_transmission: float = 0.0,
) -> ProductionHairEarOcclusion:
    """Validate the real Hair/Ear owners and delegate spatial resolution."""
    if ear.id == hair.id:
        raise ValueError("Hair/Ear owners must be distinct")
    if ear.kind != "Ear" or hair.kind != "Hair":
        raise ValueError("Hair/Ear production adapter requires Ear then Hair components")
    pair = resolve_production_pair_occlusion(
        ear, ear_geometry, ear_depth, hair, hair_geometry, hair_depth,
        occluder_opacity=hair_opacity, occluder_transmission=hair_transmission,
    )
    return ProductionHairEarOcclusion.from_pair(pair)
