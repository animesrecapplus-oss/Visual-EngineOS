# V1.87 — guarantees and status — CMP-EYE-EYEBROW

## Guaranteed after implementation

- `BrowSpec.enabled` is bool-only.
- All local numeric fields are Real, non-bool and finite/float-testable before existing range checks.
- Existing ranges and style/color validation remain unchanged.
- `BrowSpec` remains frozen and slot-based.
- Valid tested production rendering is unchanged.
- No database migration, cache algorithm or COLOR change occurred.

## Not guaranteed / not promoted

- artistic eyebrow quality;
- new eyebrow anatomy;
- automatic placement calibration;
- occlusion semantics beyond existing renderer behavior;
- a maximum eyebrow resource ceiling;
- property-based coverage.

Status: `CERTIFIED` for the documented local input-boundary scope. Certification does not promote any of the explicitly non-guaranteed claims above.
