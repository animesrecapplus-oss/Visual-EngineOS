# Iris hostile test matrix — V1.84

| ID | Attack | Expected protection | Status |
|---|---|---|---|
| ADV-IRIS-001 | NaN glow/opacity/pattern strength/outline width | reject | PASS |
| ADV-IRIS-002 | +∞ / -∞ real fields | reject | PASS |
| ADV-IRIS-003 | bool real field | reject | PASS |
| ADV-IRIS-004 | bool count | reject | PASS |
| ADV-IRIS-005 | fractional ring count | reject | PASS |
| ADV-IRIS-006 | fractional pattern count | reject | PASS |
| ADV-IRIS-007 | coercive numeric string | reject | PASS |
| ADV-IRIS-008 | negative ring count | reject | PASS |
| ADV-IRIS-009 | zero pattern count | reject | PASS |
| ADV-IRIS-010 | glow/opacity/pattern strength outside bounds | reject | PASS |
| ADV-IRIS-011 | negative outline width | reject | PASS |
| ADV-IRIS-012 | valid authored numeric values | preserve exactly | PASS |
| ADV-IRIS-013 | extremely large valid count | no invented cap; resource bound remains downstream | DECLARED |
| ADV-IRIS-014 | invalid shape vocabulary | no V1.84 contract promoted | DECLARED |
| ADV-IRIS-015 | invalid pattern vocabulary | no V1.84 contract promoted | DECLARED |
| ADV-IRIS-016 | iris/pupil containment conflict | downstream relation owner required | DECLARED |
| ADV-IRIS-017 | iris/gaze interaction | gaze owner required | DECLARED |
| ADV-IRIS-018 | iris/eyelid occlusion | visibility/occlusion owner required | DECLARED |

`DECLARED` is not counted as PASS. V1.84 does not invent a maximum count or a new morphology owner.
