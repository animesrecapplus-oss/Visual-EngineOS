# Pupil error register

## ERR-EYE-PUPIL-001 — documentation/implementation status drift
Blueprint labels are not executable proof. Corrected by explicit truth statuses.

## ERR-EYE-PUPIL-002 — interaction ownership ambiguity
Pupil interaction tasks remain explicitly owned by iris/gaze/eyelid/transform components.

## ERR-EYE-PUPIL-003 — mixed pupil/lash effects ownership
`LashShadowSpec` remains canonically owned by `lashes/effects.py`; compatibility imports are preserved.

## ERR-EYE-PUPIL-004 — incomplete finite boundary
Observed in V1.82 pre-change audit: `outline_width` was omitted from `_finite()` and bool/string coercion
could survive the helper. This violated the local numeric-state contract.

Resolution: `pupil/spec.py:24-29` now rejects non-Real/bool state and validates all eight numeric fields for finiteness.
Regression: V1.82 focused hostile suite and full regression PASS.
