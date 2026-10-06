# Invariants and assumptions — CMP-FACE-EAR

- `INV-FE-001`: all emitted coordinates are finite; `GeometryContract` enforces this.
- `INV-FE-002`: bounds contain the generated closed path envelope.
- `INV-FE-003`: `component_id` identifies the leaf owner; composite rebasing may add parent ownership separately.
- `INV-FE-004`: ear depth is not used to invent occlusion; it is only authored paint/depth metadata consumed by generic infrastructure.
- `INV-FE-005`: two-ear cardinality belongs to the HumanFace composite, not the leaf generator.
- `INV-FE-006`: the leaf generator never accepts bool, string or non-finite width/height values, even when a malformed component bypasses normal `Parameter` construction.
- `INV-FE-007`: `0.5 * width` and `0.5 * height` must remain strictly positive; positive subnormal inputs that collapse to zero-radius geometry are rejected.

Assumption: the normal face authoring contract supplies numeric `width`, `height` and `center`; missing dimensions use documented finite defaults.
