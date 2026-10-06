# V1.87 — invariants and assumptions — CMP-EYE-EYEBROW

- `INV-EYEBROW-001`: `enabled` is boolean-only.
- `INV-EYEBROW-002`: every numeric field is finite and numerically usable by downstream SVG arithmetic/formatting.
- `INV-EYEBROW-003`: existing authored numeric ranges are unchanged.
- `INV-EYEBROW-004`: `shape` vocabulary is unchanged and closed at the existing owner boundary.
- `INV-EYEBROW-005`: `BrowSpec` remains immutable.
- `INV-EYEBROW-006`: eyebrow validation does not alter eye geometry cache identity because brow styling is outside
  `_eye_cache_inputs` by verified design.

Assumptions explicitly retained from existing architecture:
- eyebrow is a periocular sibling branch, not an eyelid child;
- eye rotation is inherited by the renderer and is not reimplemented by `BrowSpec`;
- placement/gap semantics remain renderer-owned;
- no maximum eyebrow length/count resource contract is introduced.
