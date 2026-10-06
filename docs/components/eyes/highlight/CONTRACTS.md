# Contracts — CMP-EYE-HIGHLIGHT

- `CON-HIGHLIGHT-001`: `shape` accepts exactly `circle`, `ellipse`, `diamond`, `streak`; unknown or opaque values
  are rejected at construction.
- `CON-HIGHLIGHT-002`: `x`, `y`, `width`, `height`, `opacity`, `rotation_deg` must be non-bool `numbers.Real` values.
- `CON-HIGHLIGHT-003`: those numeric values must be finite; overflow or malformed finite evaluation is rejected.
- `CON-HIGHLIGHT-004`: existing ranges remain: width/height >= 0 and opacity in [0,1]. No new placement ranges.
- `CON-HIGHLIGHT-005`: `color` continues through the shared `_color` validator; no COLOR semantics change.
- `CON-HIGHLIGHT-006`: the dataclass remains frozen/slots-based and stores authored valid values without coercion.
- `CON-HIGHLIGHT-007`: valid existing constructor calls and valid SVG output remain behaviorally unchanged.
- `CON-HIGHLIGHT-008`: no database representation or migration is introduced.
