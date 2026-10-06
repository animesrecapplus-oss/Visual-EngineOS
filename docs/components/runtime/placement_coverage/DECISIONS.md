# Decisions — CMP-PCOV-001

- `DEC-PCOV-001`: select coverage-specific contract + solver because it is a bounded responsibility embedded in `runtime.placement` and already has real consumers.
- `DEC-PCOV-002`: keep `PlacementIntent` and `PlacementSolution` in `runtime.placement`; they own general placement, not coverage internals.
- `DEC-PCOV-003`: move the public `runtime.CoverageIntent` export to the canonical owner while preserving historical identity through `runtime.placement`.
- `DEC-PCOV-004`: do not introduce cache, fingerprint, persistence, COLOR or renderer semantics because no real downstream consumer requires them.
- `DEC-PCOV-005`: add strict direct-solver numeric/type validation after hostile testing exposed permissive NaN handling.
