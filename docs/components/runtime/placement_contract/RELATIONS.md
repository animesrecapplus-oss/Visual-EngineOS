# Relations — CMP-RUNTIME-PLACEMENT-CONTRACT

- `REL-PLAC-001`: `runtime.placement` remains the placement solver and compatibility facade.
- `REL-PLAC-002`: `runtime.spatial_relationships` compiles relation payloads into `PlacementIntent`.
- `REL-PLAC-003`: `runtime.placement_constraints` evaluates placement constraints around the contracts.
- `REL-PLAC-004`: `runtime.placement_visibility` consumes `PlacementSolution` to derive visibility input.
- `REL-PLAC-005`: `runtime.placement_coverage` supplies the real `CoverageIntent` contract consumed by `PlacementIntent`.
- `REL-PLAC-006`: no COLOR/cache/fingerprint/provenance/database relation is introduced.
