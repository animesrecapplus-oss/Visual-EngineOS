# Current status — V1.84

## V1.84 — Iris input-boundary hardening

`CMP-EYE-IRIS` is `IMPLEMENTED / VALIDATED` for its local IrisSpec numeric/type validation scope. Final certification is `BLOCKED` because the checkpoint archive contains no Git metadata, so repository cleanliness cannot be verified.

Canonical owner: `src/visual_engine/components/face/eyes/iris/spec.py`.

Direct semantic parent: the `EYEBALL` architectural node. Aggregate/public parent: `CMP-EYE`. Semantic child:
`CMP-EYE-PUPIL`.

The implementation rejects bool/fractional count state and non-finite/non-Real local numeric state while preserving
valid values. No geometry, renderer algorithm, cache identity, COLOR or database implementation changed.

Focused hostile tests, real consumer integration, full regression, compileall, dependency/cycle/duplicate audits,
database identity, benchmark sanity, production visual invariance and documentation line-range validation all pass.
The remaining certification blocker is repository cleanliness/state verification: no `.git` metadata exists in the
checkpoint archive, and the protocol forbids promoting an unverified repository state to PASS.

`DECLARED`: maximum count/resource ceiling, shape/pattern vocabulary, pupil containment, gaze, eyelid exposure,
corneal optics, highlights and deeper Iris morphology.
