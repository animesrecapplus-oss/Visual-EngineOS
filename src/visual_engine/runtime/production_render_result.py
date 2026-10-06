from __future__ import annotations

from dataclasses import dataclass

from visual_engine.components.common.geometry_contract import GeometryContract
from visual_engine.runtime.generation import GeometryGenerationResult
from visual_engine.runtime.production_face_overlap_visibility import ProductionVisibilityResolution
from visual_engine.runtime.production_hair_ear_occlusion import ProductionHairEarOcclusion
from visual_engine.runtime.production_head_ear_occlusion import ProductionHeadEarOcclusion
from visual_engine.runtime.resolved_component import ResolvedComponent


@dataclass(frozen=True, slots=True)
class ProductionRenderResult:
    """Immutable output envelope for one canonical production face render."""

    component_id: str
    generator: str
    resolution: ResolvedComponent
    geometry: GeometryGenerationResult
    camera_geometry: GeometryContract
    svg: str
    visibility: ProductionVisibilityResolution | None = None
    hair_ear_occlusion: tuple[ProductionHairEarOcclusion, ...] = ()
    head_ear_occlusion: tuple[ProductionHeadEarOcclusion, ...] = ()
