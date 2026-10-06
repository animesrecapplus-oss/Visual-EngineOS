from __future__ import annotations

"""Caller-owned production session boundary for one face render lifetime."""

from visual_engine.components.common.meta import Component
from visual_engine.runtime.resolution_context import ResolutionContext
from visual_engine.runtime.geometry_cache import GeometryCache
from visual_engine.runtime.graph import RuntimeGraph
from visual_engine.runtime.production_face_render import render_production_face
from visual_engine.runtime.production_geometry_service_resources import ProductionGeometryServiceResources
from visual_engine.runtime.production_render_result import ProductionRenderResult
from visual_engine.runtime.resolution_cache import ResolutionCache
from visual_engine.runtime.versioning import VersionStamp
from visual_engine.render.geometry_svg import GeometrySvgTheme
from visual_engine.scene.composition import Camera, Placement


class ProductionRenderSession:
    """Caller-owned lifetime for one production face render session.

    The session owns the graph and only caches it constructed; injected caches
    remain caller-owned. Request orchestration belongs to ``production_face_render``.
    """

    def __init__(
        self,
        root: Component,
        *,
        geometry_cache: GeometryCache | None = None,
        resolution_cache: ResolutionCache | None = None,
    ) -> None:
        if not isinstance(root, Component):
            raise TypeError("ProductionRenderSession root must be a Component")
        self._root: Component | None = root
        self._graph: RuntimeGraph | None = RuntimeGraph.from_component(root)
        self._owns_geometry_cache = geometry_cache is None
        self._owns_resolution_cache = resolution_cache is None
        self._geometry_cache = geometry_cache if geometry_cache is not None else GeometryCache()
        self._resolution_cache = resolution_cache if resolution_cache is not None else ResolutionCache()
        self._resources = ProductionGeometryServiceResources(self._geometry_cache)
        self._closed = False

    @property
    def graph(self) -> RuntimeGraph:
        self._ensure_open()
        assert self._graph is not None
        return self._graph

    @property
    def geometry_cache(self) -> GeometryCache:
        self._ensure_open()
        return self._geometry_cache

    @property
    def resolution_cache(self) -> ResolutionCache:
        self._ensure_open()
        return self._resolution_cache

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("ProductionRenderSession is closed")

    def render_face(
        self,
        component_id: str,
        *,
        placement: Placement | None = None,
        camera: Camera | None = None,
        generator: str = "face.human_with_eyes_nose_mouth_ears_hair",
        context: ResolutionContext | None = None,
        version: VersionStamp | None = None,
        theme: GeometrySvgTheme | None = None,
    ) -> ProductionRenderResult:
        """Delegate one validated production request to the canonical renderer owner."""
        self._ensure_open()
        graph = self.graph
        if not graph.is_current():
            raise RuntimeError("ProductionRenderSession graph is stale; call refresh() before rendering")
        assert self._root is not None
        return render_production_face(
            self._root,
            graph,
            self._resources,
            self._resolution_cache,
            component_id,
            placement=placement,
            camera=camera,
            generator=generator,
            context=context,
            version=version,
            theme=theme,
        )

    def refresh(self) -> None:
        """Recompile topology after an intentional authoring-tree mutation."""
        self._ensure_open()
        assert self._graph is not None
        self._graph = self._graph.rebuild()

    def close(self) -> None:
        """Release the graph and only the caches whose lifetime this session owns."""
        if self._closed:
            return
        if self._owns_geometry_cache:
            self._geometry_cache.clear()
        if self._owns_resolution_cache:
            self._resolution_cache.clear()
        self._resources.close()
        self._graph = None
        self._root = None
        self._closed = True

    def __enter__(self) -> "ProductionRenderSession":
        self._ensure_open()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
