# Decisions

`DEC-PRS-001`: V1.71 fresh audit selects `ProductionRenderSession` as one independent lifecycle responsibility already bounded by a 118-line class and real public/integration consumers.
`DEC-PRS-002`: extract only the session class; request orchestration remains in `production_face_render` and geometry-service semantics remain in their owner.
`DEC-PRS-003`: preserve `production_slice.ProductionRenderSession` as an identity-compatible compatibility import.
`DEC-PRS-004`: move the public runtime import to the canonical owner while retaining the compatibility facade.
`DEC-PRS-005`: keep cache construction/ownership in the session; injected caches remain caller-owned.
`DEC-PRS-006`: freeze COLOR, database, persistence, fingerprint algorithms and renderer semantics.
