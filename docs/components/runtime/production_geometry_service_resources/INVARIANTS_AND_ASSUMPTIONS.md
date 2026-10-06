# Invariants and assumptions

`INV-GSR-001`: the supplied cache remains the canonical `ProductionRenderSession` cache owner.

`INV-GSR-002`: the resource never clears or mutates cache ownership state.

`INV-GSR-003`: exactly one production registry/service pair is created per resource instance.

`INV-GSR-004`: a closed resource cannot expose its released geometry service.

`INV-GSR-005`: repeated `close()` calls are harmless.

`INV-GSR-006`: the existing production registry contents and generator selection remain unchanged.

`INV-GSR-007`: geometry/resolution cache statistics and generated SVG bytes remain identical to V1.65.

Assumption: `CachedGeometryGenerator` remains the existing canonical production geometry service;
this brick does not change its generation or cache semantics.
