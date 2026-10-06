# Invariants and assumptions — CMP-EYE-HIGHLIGHT

- `INV-HIGHLIGHT-001`: runtime shape vocabulary is closed to the four existing renderer branches.
- `INV-HIGHLIGHT-002`: no boolean can enter a numeric ReflectionMark field.
- `INV-HIGHLIGHT-003`: no non-Real numeric value or coercive numeric string enters the owner.
- `INV-HIGHLIGHT-004`: no non-finite or float-unrepresentable numeric value survives construction.
- `INV-HIGHLIGHT-005`: width/height and opacity retain their pre-V1.88 ranges.
- `INV-HIGHLIGHT-006`: valid authored color semantics and immutable value-object behavior remain unchanged.
- `INV-HIGHLIGHT-007`: ReflectionMark fields remain outside `_eye_cache_inputs`; highlight styling does not become geometry identity.
- `INV-HIGHLIGHT-008`: visibility remains owned by `EyeVisibilitySpec`; this brick does not alter visibility hierarchy.

Assumption explicitly retained: `numbers.Real` is the local numeric acceptance boundary, matching the hardened ocular
specification pattern; no string-to-number coercion is performed.
