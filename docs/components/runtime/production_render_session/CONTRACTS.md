# Contracts

`CON-PRS-001`: `ProductionRenderSession` is the sole canonical class owner.
`CON-PRS-002`: injected `GeometryCache` and `ResolutionCache` remain caller-owned across session close.
`CON-PRS-003`: session-created caches are cleared on close.
`CON-PRS-004`: a stale `RuntimeGraph` fails closed before a render and `refresh()` rebuilds it.
`CON-PRS-005`: `render_face()` delegates the request to `production_face_render.render_production_face` without reconstructing its result or changing its semantics.
`CON-PRS-006`: `production_slice.ProductionRenderSession` remains identity-compatible with the canonical owner.
`CON-PRS-007`: `runtime.ProductionRenderSession` resolves to the canonical owner.
