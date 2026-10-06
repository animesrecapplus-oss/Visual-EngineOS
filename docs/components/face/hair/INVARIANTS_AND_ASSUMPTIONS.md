# Invariants and assumptions — CMP-FACE-HAIR

- `INV-FH-001`: width/height are finite and > 0.
- `INV-FH-002`: generated path is closed and has deterministic command order.
- `INV-FH-003`: exactly one surface owns the path and identifies the Hair component.
- `INV-FH-004`: no negative `depth_layer` is emitted.
- `INV-FH-005`: geometry fingerprint changes when the Hair component parameters change through the existing cache path.
- `INV-FH-006`: visibility is resolved by the generic visual contract, not by Hair geometry.

Assumption: the first production slice needs a readable cap, not strand-level anatomy.
Assumption: Hair/ear occlusion remains deferred until a real interaction consumer exists.
