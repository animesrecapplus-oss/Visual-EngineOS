# Contracts — CMP-EYE-GAZE

- `CON-GAZE-001`: `x`, `y`, `strength`, `amplitude` are non-bool `Real` values.
- `CON-GAZE-002`: those four numeric fields are finite before range checks.
- `CON-GAZE-003`: `strength` and `amplitude` remain non-negative; no new upper bound is introduced.
- `CON-GAZE-004`: `direction` remains the existing nine-value runtime vocabulary.
- `CON-GAZE-005`: `target` is either `None` or a tuple of exactly two non-bool finite `Real` values.
- `CON-GAZE-006`: valid authored values are preserved without numeric/string coercion.
- `CON-GAZE-007`: the value object remains `frozen=True, slots=True`; no persistence contract is introduced.

Preconditions: constructor receives values satisfying the above types/bounds.
Postconditions: malformed values raise `ValueError`; valid values retain their authored representation.

Effects: constructor validation only; no external mutation or I/O.
Determinism: same authored valid values produce equal deterministic objects.
Temporal behavior: none; no time/FPS dependency.
Numeric behavior: non-finite and float-overflowing numeric inputs fail closed.
Compatibility: existing valid tuple targets, directions, strengths and amplitudes remain accepted.
Performance: local validation only; no new cache/database operation.
