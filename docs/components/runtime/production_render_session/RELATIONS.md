# Relations

`REL-PRS-001`: `runtime.__init__ → ProductionRenderSession` — public API export.
`REL-PRS-002`: `production_slice → ProductionRenderSession` — compatibility import.
`REL-PRS-003`: `ProductionRenderSession → RuntimeGraph` — session-owned topology lifetime.
`REL-PRS-004`: `ProductionRenderSession → GeometryCache/ResolutionCache` — ownership boundary.
`REL-PRS-005`: `ProductionRenderSession → ProductionGeometryServiceResources` — geometry-service lifecycle.
`REL-PRS-006`: `ProductionRenderSession → production_face_render.render_production_face` — one-way request delegation.
`REL-PRS-007`: `production_face_render → ProductionRenderResult` — result ownership remains outside the session.
