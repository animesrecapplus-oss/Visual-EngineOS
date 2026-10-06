# CMP-EYE-EYELID — contracts

- `CON-EYELID-001`: all four enable controls are actual `bool`; non-bool values are rejected.
- `CON-EYELID-002`: all twelve numeric appearance controls are `Real`, non-bool and finite.
- `CON-EYELID-003`: existing numeric ranges remain unchanged: widths/offsets/crease-widths >= 0; opacities in
  [0,1]; crease lengths in (0,1].
- `CON-EYELID-004`: existing `_color` validation remains authoritative for crease/upper/lower colors.
- `CON-EYELID-005`: `EyelidAppearance` remains frozen and slot-based.

No new maximum, geometric proportion, occlusion, visibility, gaze, cache or persistence contract is promoted.

Expected errors: `TypeError` for non-bool enable controls; `ValueError` for malformed numeric state or existing range
violations; existing color errors remain unchanged.
