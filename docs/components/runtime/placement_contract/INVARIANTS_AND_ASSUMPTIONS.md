# Invariants and assumptions — CMP-RUNTIME-PLACEMENT-CONTRACT

- `INV-PLAC-001`: every contract instance is immutable after construction.
- `INV-PLAC-002`: all contract numeric inputs that require finiteness reject NaN and infinity.
- `INV-PLAC-003`: front/behind/coplanar depth offset semantics cannot contradict the selected relation.
- `INV-PLAC-004`: a placement solution cannot contain non-positive scales or invalid target fractions.
- `INV-PLAC-005`: diagnostics have deterministic key ordering.
- `INV-PLAC-006`: there is one canonical owner for every extracted placement contract type.
- `INV-PLAC-007`: solver behavior remains in `runtime.placement`; extraction cannot alter placement math.

Assumption: geometry validity and anchor existence remain checked against `GeometryContract` by the solver/materialization layer.
