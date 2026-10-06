# Errors — CMP-EYE-GAZE

- `ERR-GAZE-001`: numeric bool/string coercion was accepted before V1.89.
- `ERR-GAZE-002`: huge integer conversion could leak `OverflowError` from the shared float conversion.
- `ERR-GAZE-003`: target strings/bools could cross the constructor and fail later during vector/transform arithmetic.
- `ERR-GAZE-004`: mutable list targets could be stored despite the declared tuple boundary.

V1.89 converts these malformed authored states into explicit local `ValueError` rejection.
No new exception class is introduced.
