# Errors — CMP-EYE-HIGHLIGHT

Pre-change defects reproduced against the exact V1.87 source:

- `ERR-HIGHLIGHT-001`: numeric strings such as `x="0.2"` were accepted and remained strings.
- `ERR-HIGHLIGHT-002`: booleans such as `x=True` and `opacity=True` were accepted as numeric values.
- `ERR-HIGHLIGHT-003`: `10**10000` could leak `OverflowError` from shared `_finite` instead of a domain validation error.
- `ERR-HIGHLIGHT-004`: unknown `shape="triangle"` was accepted; renderer would route it to the non-circle/non-ellipse/non-diamond
  branch, effectively treating it as the streak/rect form.

No new error class is introduced. V1.88 converts these malformed authored states into explicit local `ValueError` rejection.
