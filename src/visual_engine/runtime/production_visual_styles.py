from __future__ import annotations

"""Production style resolution for renderer-visible geometry owners.

This module owns the existing style-map construction that was previously
embedded in ``ProductionRenderSession.render_face``. It delegates appearance
resolution to the canonical component resolver and never mutates geometry.
"""

from visual_engine.components.common.geometry_contract import GeometryContract
from visual_engine.components.common.visual_contract import ResolvedVisualContract
from visual_engine.runtime.contract import resolve_component
from visual_engine.runtime.resolution_context import ResolutionContext
from visual_engine.runtime.graph import RuntimeGraph
from visual_engine.runtime.resolution_cache import ResolutionCache
from visual_engine.runtime.versioning import VersionStamp


def resolve_production_visual_styles(
    graph: RuntimeGraph,
    component_id: str,
    camera_geometry: GeometryContract,
    root_visual: ResolvedVisualContract,
    *,
    context: ResolutionContext | None = None,
    version: VersionStamp | None = None,
    cache: ResolutionCache | None = None,
) -> dict[str, ResolvedVisualContract]:
    """Build the renderer style map in the former caller's stable order.

    The caller supplies the already-resolved root visual so this adapter does not
    duplicate the production resolution/cache lookup. The generic resolver remains
    the sole owner of inheritance, effects and fingerprints.
    """
    if not isinstance(graph, RuntimeGraph):
        raise TypeError("production style resolution requires a RuntimeGraph")
    if not isinstance(component_id, str) or not component_id:
        raise ValueError("component_id must be a non-empty string")
    if not isinstance(camera_geometry, GeometryContract):
        raise TypeError("camera_geometry must be a GeometryContract")
    if not isinstance(root_visual, ResolvedVisualContract):
        raise TypeError("root_visual must be a ResolvedVisualContract")
    if context is not None and not isinstance(context, ResolutionContext):
        raise TypeError("context must be a ResolutionContext or None")
    if version is not None and not isinstance(version, VersionStamp):
        raise TypeError("version must be a VersionStamp or None")
    if cache is not None and not isinstance(cache, ResolutionCache):
        raise TypeError("cache must be a ResolutionCache or None")

    styles: dict[str, ResolvedVisualContract] = {component_id: root_visual}
    owner_ids = {
        str(primitive.data["component_id"])
        for primitive in camera_geometry.primitives
        if primitive.data.get("component_id")
    }
    owner_ids.update(
        str(surface.data["source_component_id"])
        for surface in camera_geometry.surfaces
        if surface.data.get("source_component_id")
    )
    for owner_id in sorted(owner_ids):
        if owner_id == component_id or owner_id not in graph.nodes:
            continue
        styles[owner_id] = resolve_component(
            graph, owner_id, context=context, version=version, cache=cache
        ).visual
    return styles
