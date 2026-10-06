from __future__ import annotations

"""Canonical orchestration owner for one production face render request.

The session owns lifetime/caches; this module owns the request pipeline and
immutable result assembly. Existing geometry, appearance, renderer and
relation owners remain canonical and are called exactly once from this path.
"""

from visual_engine.components.common.geometry_contract import GeometryContract
from visual_engine.components.common.meta import Component
from visual_engine.components.common.visual_contract import ResolvedVisualContract
from visual_engine.render.geometry_svg import GeometrySvgTheme, render_geometry_svg
from visual_engine.runtime.contract import resolve_component
from visual_engine.runtime.resolved_component import ResolvedComponent
from visual_engine.runtime.resolution_context import ResolutionContext
from visual_engine.runtime.generation import GeometryGenerationResult
from visual_engine.runtime.geometry_transform import resolve_geometry_contract
from visual_engine.runtime.graph import RuntimeGraph
from visual_engine.runtime.production_face_overlap_relations import (
    ProductionVisibilityResolution,
    resolve_production_face_overlap_relations,
)
from visual_engine.runtime.production_geometry_service_resources import ProductionGeometryServiceResources
from visual_engine.runtime.production_hair_ear_occlusion import ProductionHairEarOcclusion
from visual_engine.runtime.production_hair_ear_relations import resolve_production_hair_ear_relations
from visual_engine.runtime.production_head_ear_occlusion import ProductionHeadEarOcclusion
from visual_engine.runtime.production_head_ear_relations import resolve_production_head_ear_relations
from visual_engine.runtime.production_owner_geometry import extract_production_owner_geometry
from visual_engine.runtime.production_render_result import ProductionRenderResult
from visual_engine.runtime.production_visual_styles import resolve_production_visual_styles
from visual_engine.runtime.resolution_cache import ResolutionCache
from visual_engine.runtime.versioning import VersionStamp
from visual_engine.scene.composition import Camera, Placement



def render_production_face(
    root: Component,
    graph: RuntimeGraph,
    resources: ProductionGeometryServiceResources,
    resolution_cache: ResolutionCache,
    component_id: str,
    *,
    placement: Placement | None = None,
    camera: Camera | None = None,
    generator: str,
    context: ResolutionContext | None = None,
    version: VersionStamp | None = None,
    theme: GeometrySvgTheme | None = None,
) -> ProductionRenderResult:
    """Execute the existing end-to-end production face render pipeline."""
    if not isinstance(root, Component):
        raise TypeError("production face render root must be a Component")
    if not isinstance(graph, RuntimeGraph):
        raise TypeError("production face render graph must be a RuntimeGraph")
    if not isinstance(resources, ProductionGeometryServiceResources):
        raise TypeError("production face render resources are invalid")
    if not isinstance(resolution_cache, ResolutionCache):
        raise TypeError("production face render resolution_cache must be ResolutionCache")
    if not isinstance(component_id, str) or not component_id:
        raise ValueError("component_id must be a non-empty string")
    if not isinstance(generator, str) or not generator:
        raise ValueError("generator must be a non-empty string")
    if context is not None and not isinstance(context, ResolutionContext):
        raise TypeError("context must be ResolutionContext or None")
    if version is not None and not isinstance(version, VersionStamp):
        raise TypeError("version must be VersionStamp or None")

    version = version or VersionStamp()
    context = context or ResolutionContext()
    resolution = resolve_component(graph, component_id, context=context, version=version, cache=resolution_cache)
    generated = resources.geometry_service.generate(graph, component_id, generator=generator, version=version)
    camera_geometry = resolve_geometry_contract(
        graph, component_id, generated.geometry, placement=placement, camera=camera,
        target="camera" if camera is not None else "scene",
    )
    styles: dict[str, ResolvedVisualContract] = resolve_production_visual_styles(
        graph, component_id, camera_geometry, resolution.visual,
        context=context, version=version, cache=resolution_cache,
    )
    svg = render_geometry_svg(camera_geometry, styles=styles, theme=theme)
    overlap = resolve_production_face_overlap_relations(
        root, camera_geometry, generator, owner_geometry=extract_production_owner_geometry
    )
    hair_ear: tuple[ProductionHairEarOcclusion, ...] = ()
    head_ear: tuple[ProductionHeadEarOcclusion, ...] = ()
    if generator == "face.human_with_eyes_nose_mouth_ears_hair":
        hair_ear = resolve_production_hair_ear_relations(
            root, camera_geometry, styles, owner_geometry=extract_production_owner_geometry
        )
        head_ear = resolve_production_head_ear_relations(
            root, camera_geometry, styles[component_id], owner_geometry=extract_production_owner_geometry
        )
    return ProductionRenderResult(component_id, generator, resolution, generated, camera_geometry, svg, overlap, hair_ear, head_ear)
