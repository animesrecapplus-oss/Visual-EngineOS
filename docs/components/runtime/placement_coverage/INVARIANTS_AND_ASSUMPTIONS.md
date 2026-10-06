# Invariants and assumptions — CMP-PCOV-001

- `INV-PCOV-001`: coverage is an area fraction, never a pixel or descriptor value.
- `INV-PCOV-002`: the scale search preserves the historical low/high initialization and binary-search order.
- `INV-PCOV-003`: scale/rotation occur around the source anchor before translation to the target anchor.
- `INV-PCOV-004`: source and target regions must have positive area.
- `INV-PCOV-005`: source and target anchors must be contained by their regions; boundary anchors are allowed.
- `INV-PCOV-006`: fixed orientation/offset plus contained anchors is the precondition for the monotone nested-scale assumption.
- `INV-PCOV-007`: no object category is inspected by the solver.
- `INV-PCOV-008`: invalid numeric inputs fail before Shapely receives NaN/∞ transform parameters.

Assumption status: these assumptions are executable-tested; no unverified monotonicity claim is used outside the explicit precondition.
