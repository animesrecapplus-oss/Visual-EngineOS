# Iris guarantees and status — V1.84

## Guarantees

1. Invalid local IrisSpec numeric state fails at construction.
2. Count fields cannot be bool or fractional numeric values.
3. Real-valued local fields cannot be NaN or infinite.
4. Glow, opacity and pattern strength remain bounded; outline width remains non-negative.
5. Shared colour validation remains authoritative.
6. Valid authored IrisSpec values remain unchanged and immutable.
7. No V1.84 change alters cache identity, renderer algorithm, COLOR or database state.

## Status

`IMPLEMENTED`: local IrisSpec validation boundary.
`INTEGRATED`: verified aggregate/style/generator/renderer/compatibility consumers remain exercised.
`VISUAL_INVARIANCE`: valid production rendering remains unchanged.
`CERTIFICATION`: BLOCKED because Git repository cleanliness/state is not verifiable from the archive.
`DECLARED`: count resource ceiling, shape/pattern vocabulary, pupil containment, gaze, eyelid exposure, corneal
optics, highlights and deeper iris morphology.
