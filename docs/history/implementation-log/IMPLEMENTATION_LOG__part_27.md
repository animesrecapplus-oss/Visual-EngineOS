# Implementation log — V1.91

## Brick

`CMP-FACE-EYE-BILATERAL` — HumanFace→Eye bilateral identity propagation correction.

## Work performed

Reopened V1.89, incorporated the V1.90 audit-only result, reproduced the left-eye defect, traced the real production path, and rejected Gaze/renderer ownership.

The canonical Eye generator now derives `side` only for the existing parented HumanFace identities `left_eye` and `right_eye`. Standalone and unrelated Eye IDs retain `single`.

The stale unused `_eye_component_inputs` helper was removed from `face/generators.py` so the project does not retain two competing boundaries.

The Eye geometry generator version changed from `9` to `10`. Existing cache projection already contains `side`, so no cache algorithm change was required.

## Validation

Focused V1.91 tests, ocular/production tests, `tests/components`, `tests/integration`, compileall, dependency graph, DB identity and cache identity passed. Four production visual cases were rendered and inspected.

The complete monolithic current suite was attempted but exceeded the available execution wall-clock limit. This is recorded as a certification limitation, not converted into PASS.

## Scope exclusions

No Gaze, camera, renderer clipping/mask, COLOR, persistence, prompt compiler or generic Component-side architecture was modified.
