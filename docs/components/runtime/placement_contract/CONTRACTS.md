# Contracts — CMP-RUNTIME-PLACEMENT-CONTRACT

- `CON-PLAC-001`: scale/depth enums are closed string-valued sets.
- `CON-PLAC-002`: anchor names and source/target IDs are non-empty.
- `CON-PLAC-003`: numeric intent fields are finite; depth semantics are mutually consistent.
- `CON-PLAC-004`: dimension ratios are finite and strictly positive.
- `CON-PLAC-005`: dimension and coverage constraints cannot be requested together; coverage requires uniform scale.
- `CON-PLAC-006`: `PlacementSolution` is immutable and contains finite positive scales and valid coverage values.
- `CON-PLAC-007`: solution diagnostics are deterministically sorted.
- `CON-PLAC-008`: legacy `runtime.placement` imports remain aliases of the canonical contract owner.
