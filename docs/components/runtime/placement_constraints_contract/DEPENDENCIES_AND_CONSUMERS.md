# Dependencies and consumers — CMP-RUNTIME-PLACEMENT-CONSTRAINT-CONTRACT

## Dependencies

The owner imports only standard-library dataclass/enum/math/typing facilities. `PlacementSolution` is TYPE_CHECKING-only, so the contract owner does not depend at runtime on the placement algorithm.

## Consumers

- `CON-PCON-001`: `runtime.spatial_relationships` imports `PlacementConstraintSet` and constructs the constraint declarations.
- `CON-PCON-002`: `runtime.spatial_relationships` imports individual constraint types while parsing relation payloads.
- `CON-PCON-003`: `runtime.__init__` exposes the canonical contracts.
- `CON-PCON-004`: `tests/unit/test_v13_placement_constraints.py` consumes the historical public contract surface.
