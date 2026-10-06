# Decisions

`DEC-PRR-001`: select the existing immutable production result envelope because the fresh V1.69 audit proves a distinct
output-contract responsibility with real producer, public and test consumers.

`DEC-PRR-002`: move only the dataclass; keep request orchestration in `production_face_render`.

`DEC-PRR-003`: preserve `production_slice.ProductionRenderResult` and `runtime.ProductionRenderResult` identity.

`DEC-PRR-004`: preserve positional field order because the canonical producer currently uses positional construction.

`DEC-PRR-005`: freeze COLOR, database, persistence, cache/fingerprint algorithms and renderer semantics.
