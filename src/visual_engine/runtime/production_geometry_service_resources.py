from __future__ import annotations

"""Session-local geometry registry/service lifecycle."""

from visual_engine.components.face.production_registry import production_face_geometry_registry
from visual_engine.runtime.generation import CachedGeometryGenerator
from visual_engine.runtime.generators import GeometryGeneratorRegistry
from visual_engine.runtime.geometry_cache import GeometryCache


class ProductionGeometryServiceResources:
    """Own the production geometry registry/service, not the caller's cache.

    ``ProductionRenderSession`` remains the canonical cache owner. This boundary
    only releases the registry/service references it creates for that cache.
    """

    def __init__(self, geometry_cache: GeometryCache) -> None:
        if not isinstance(geometry_cache, GeometryCache):
            raise TypeError("geometry_cache must be GeometryCache")
        self._registry: GeometryGeneratorRegistry | None = production_face_geometry_registry()
        self._geometry_service: CachedGeometryGenerator | None = CachedGeometryGenerator(
            self._registry, geometry_cache
        )
        self._closed = False

    @property
    def geometry_service(self) -> CachedGeometryGenerator:
        if self._closed or self._geometry_service is None:
            raise RuntimeError("ProductionGeometryServiceResources is closed")
        return self._geometry_service

    def close(self) -> None:
        """Release service/registry references without clearing the session cache."""
        if self._closed:
            return
        self._geometry_service = None
        self._registry = None
        self._closed = True
