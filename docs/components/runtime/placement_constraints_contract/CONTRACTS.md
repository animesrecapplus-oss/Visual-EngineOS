# Contracts — CMP-RUNTIME-PLACEMENT-CONSTRAINT-CONTRACT

- `CON-PCON-001`: `ConstraintStatus` is the closed satisfied/violated status set.
- `CON-PCON-002`: each constraint value validates finite, non-negative tolerances/distances.
- `CON-PCON-003`: `PlacementConstraintSet` is frozen and normalizes metadata deterministically.
- `CON-PCON-004`: `ConstraintCheck` records measured value, limit and status without mutation.
- `CON-PCON-005`: `ConstrainedPlacementSolution` sorts checks deterministically and rejects violated checks.
- `CON-PCON-006`: legacy imports remain aliases of the canonical owner.
