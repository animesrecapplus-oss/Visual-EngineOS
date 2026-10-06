# Impact map — CMP-PCOV-001

- `IMP-PCOV-001` source: extract coverage contract and solver from `runtime.placement`.
- `IMP-PCOV-002` consumers: `placement`, `spatial_relationships`, public runtime export.
- `IMP-PCOV-003` parent/siblings: general placement remains owner of anchor/dimension/rotation/depth; constraints and visibility remain separate.
- `IMP-PCOV-004` cache/fingerprint/provenance: no real consumer or algorithm touched; frozen.
- `IMP-PCOV-005` persistence/database: no placement persistence consumer/schema found; no migration.
- `IMP-PCOV-006` determinism: preserve search bounds, doubling, tolerance stop and iteration order.
- `IMP-PCOV-007` visual: placement can affect rendering, so production render identity was compared in normal/boundary/interaction cases.
- `IMP-PCOV-008` unchanged behavior: public `CoverageIntent` identity, `PlacementSolution` values and relation compilation remain equivalent to V1.73.
