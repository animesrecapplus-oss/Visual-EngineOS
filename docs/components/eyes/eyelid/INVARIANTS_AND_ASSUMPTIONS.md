# CMP-EYE-EYELID — invariants and assumptions

- `INV-EYELID-001`: boolean controls cannot carry integer/string truthiness.
- `INV-EYELID-002`: numeric appearance state is finite before range comparison.
- `INV-EYELID-003`: existing authored numeric ranges are preserved exactly.
- `INV-EYELID-004`: valid authored values remain immutable after construction.
- `INV-EYELID-005`: validation does not mutate geometry, cache, visibility or renderer state.

Assumptions are limited to existing source evidence: the current range checks define the accepted numeric domains;
no resource ceiling or new anatomical ratio is inferred from them.
