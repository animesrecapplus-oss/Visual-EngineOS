# Invariants and assumptions

`INV-POG-001`: exactly one non-empty owner identity is requested per call.
`INV-POG-002`: at least one matching surface is required.
`INV-POG-003`: all selected depth layers must collapse to one integer value.
`INV-POG-004`: every selected path index is bounds-checked before indexing.
`INV-POG-005`: path rebasing is deterministic in source-surface order and does not mutate the input contract.
`INV-POG-006`: returned depth is finite because the source `GeometryContract` rejects non-finite metadata.
`INV-POG-007`: no resolution/cache/render side effect occurs.

Assumption: `GeometryContract` remains the authoritative validator for nested geometry metadata.
