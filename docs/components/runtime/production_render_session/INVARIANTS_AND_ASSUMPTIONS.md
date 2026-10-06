# Invariants and assumptions

`INV-PRS-001`: exactly one canonical `ProductionRenderSession` class owner exists.
`INV-PRS-002`: closed sessions cannot expose graph/cache state or render/refresh.
`INV-PRS-003`: session teardown clears only caches whose ownership flags are true.
`INV-PRS-004`: injected caches survive session teardown unchanged.
`INV-PRS-005`: graph freshness is checked before production rendering.
`INV-PRS-006`: refresh rebuilds the graph but does not replace caller-injected caches.
`INV-PRS-007`: session teardown closes `ProductionGeometryServiceResources` exactly once.

Assumption: the existing `production_face_render` contract remains the sole request-pipeline owner.
