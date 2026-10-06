# Invariants and assumptions — CMP-EYE-GAZE

- `INV-GAZE-001`: authored numeric fields cannot be bools or non-Real values.
- `INV-GAZE-002`: authored numeric fields are finite before solver/transform arithmetic.
- `INV-GAZE-003`: strength/amplitude are non-negative exactly as before V1.89.
- `INV-GAZE-004`: direction vocabulary is closed at the constructor boundary.
- `INV-GAZE-005`: target, when present, is an immutable two-element numeric tuple.
- `INV-GAZE-006`: no numeric coercion changes authored values.
- `INV-GAZE-007`: valid gaze semantics and cache identity remain unchanged.

Assumptions explicitly retained from existing architecture:
- Gaze controls the internal ocular assembly, not the eye envelope.
- Higher-level 3D/optical systems remain above `GazeSolver`.
- The shared `_finite` helper remains required by `BinocularGazeSolver` and is not changed by V1.89.
