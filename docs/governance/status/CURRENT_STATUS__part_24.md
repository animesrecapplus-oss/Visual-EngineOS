# Current status — V1.82

## V1.82 — Pupil local input-boundary hardening

V1.82 restarted from the certified V1.81 checkpoint and repeated the complete read-only selection audit.
The archive hygiene discrepancy (`.pytest_cache` present in the V1.81 ZIP despite the prior purge claim) was
recorded rather than hidden; the archive has no Git metadata, so Git cleanliness is not claimed.

`CMP-EYE-PUPIL` was selected as a different mature micro-component. It has a real owner, parent/child boundary,
real consumers, existing contracts/invariants, cache impact mapping, public compatibility exports and focused tests.
A real malformed-state defect was reproduced before modification: `outline_width` omitted from finite validation,
plus bool/string coercion through the shared `_finite(float(...))` helper.

V1.82 changes only `src/visual_engine/components/face/eyes/pupil/spec.py:1-31` and adds focused hostile tests.
Valid PupilSpec values, geometry semantics, cache algorithm, COLOR, persistence/database and renderer policy remain unchanged.

Status: `V1.82 / CMP-EYE-PUPIL / CERTIFIED` only after the complete gate and release ZIP integrity proof.
