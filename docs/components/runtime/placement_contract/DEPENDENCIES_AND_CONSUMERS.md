# Dependencies and consumers — CMP-RUNTIME-PLACEMENT-CONTRACT

## Dependencies

The owner depends on standard-library dataclasses/enums/math plus the real `CoverageIntent` contract from `runtime.placement_coverage`.

## Direct production consumers

- `CON-PLAC-009`: `runtime.spatial_relationships` constructs placement intents and consumes placement solutions.
- `CON-PLAC-010`: `runtime.placement_constraints` validates/solves intents and solutions.
- `CON-PLAC-011`: `runtime.placement_visibility` consumes `PlacementSolution`.
- `CON-PLAC-012`: `runtime.__init__` exposes the public contract names.

## Test consumers

Historical placement, relation-placement, constraint and placement-visibility suites consume the legacy API.
