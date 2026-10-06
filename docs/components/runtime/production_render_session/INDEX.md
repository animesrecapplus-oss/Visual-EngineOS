# `CMP-RUNTIME-PRODUCTION-RENDER-SESSION`

Identity: immutable ownership is not claimed; this is the caller-owned production session lifecycle boundary.

Owner: `src/visual_engine/runtime/production_render_session.py:18-118`.
Parent: production runtime public boundary exposed by `runtime.__init__`.
Children: no child micro-component; the session references `RuntimeGraph`, `GeometryCache`, `ResolutionCache` and `ProductionGeometryServiceResources` without owning their semantic contracts.
Siblings: production face request orchestration, result contract, geometry-service resources, visual styles, overlap relations, Hair/Ear relations and Head/Ear relations.

Compatibility: `production_slice.py:7` re-exports the canonical class; `runtime.__init__.py:254` is the public export.
