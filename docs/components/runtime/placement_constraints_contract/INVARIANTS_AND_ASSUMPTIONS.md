# Invariants and assumptions — CMP-RUNTIME-PLACEMENT-CONSTRAINT-CONTRACT

- `INV-PCON-001`: contract instances are immutable after construction.
- `INV-PCON-002`: all numeric constraint thresholds are finite and non-negative.
- `INV-PCON-003`: metadata ordering is deterministic.
- `INV-PCON-004`: there is one canonical owner for each extracted contract type.
- `INV-PCON-005`: violated checks cannot be embedded in `ConstrainedPlacementSolution`.
- `INV-PCON-006`: contract extraction must not alter placement or geometry semantics.

Assumption: geometry validity remains owned by `GeometryContract`/materialization and constraint evaluation remains owned by `placement_constraints.py`.
