# V1.87 — contracts — CMP-EYE-EYEBROW

- `CON-EYEBROW-001`: `enabled` is a real `bool`; non-bool values are rejected.
- `CON-EYEBROW-002`: all numeric authored fields are `Real`, not `bool`, and finite/float-representable before range checks.
- `CON-EYEBROW-003`: existing ranges remain authoritative: length/thickness >= 0; density/ornament/fades in [0,1];
  min gap >= 0 and max gap >= min gap.
- `CON-EYEBROW-004`: `shape` remains restricted to the existing `BrowStyle` vocabulary; no new style is introduced.
- `CON-EYEBROW-005`: `color` continues through the shared `_color` validator.
- `CON-EYEBROW-006`: `BrowSpec` remains frozen/slot-based and immutable.

### Input/output

Input: constructor field values. Output: an immutable `BrowSpec` or a deterministic validation exception.
No side effects, persistence writes, cache mutation or renderer calls occur during validation.

### Error semantics

Invalid boolean type → `TypeError`. Invalid numeric type/finiteness → `ValueError`. Existing range/style/color errors
remain `ValueError`. Huge integers that cannot be safely converted for finite numeric validation are rejected rather
than leaking `OverflowError` from the validator.

### Determinism/compatibility

Equal valid inputs produce equal value objects. Existing valid authored values and public import paths remain unchanged.
No temporal or seed-dependent behavior exists at this boundary.
