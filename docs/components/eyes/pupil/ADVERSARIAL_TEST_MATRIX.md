# Pupil hostile test matrix

| ID | Attack | Expected protection | Status |
|---|---|---|---|
| ADV-PUPIL-001 | NaN/∞ including outline width | reject `ValueError` | PASS |
| ADV-PUPIL-002 | zero/negative scale | reject `ValueError` | PASS |
| ADV-PUPIL-003 | opacity outside bounds | reject `ValueError` | PASS |
| ADV-PUPIL-004 | malformed colours | reject shared validator error | PASS |
| ADV-PUPIL-005 | negative effect dimensions | reject `ValueError` | PASS |
| ADV-PUPIL-006 | effect intensity >1 | reject `ValueError` | PASS |
| ADV-PUPIL-007 | smoke wisps <1 | reject `ValueError` | PASS |
| ADV-PUPIL-008 | mutable post-construction state | frozen dataclass blocks assignment | PASS |
| ADV-PUPIL-009 | extreme finite offsets | preserve finite construction | PASS |
| ADV-PUPIL-010 | bool numeric PupilSpec state | reject `ValueError` | PASS |
| ADV-PUPIL-011 | coercive string PupilSpec state | reject `ValueError` | PASS |
| ADV-PUPIL-012 | pupil/iris containment conflict | downstream owner required | DECLARED |
| ADV-PUPIL-013 | pupil/gaze interaction | downstream owner required | DECLARED |
| ADV-PUPIL-014 | pupil/eyelid exposure | downstream owner required | DECLARED |
| ADV-PUPIL-015 | transform NaN/∞ propagation | transform owner required | DECLARED |
| ADV-PUPIL-016 | cache fingerprint omission | cache owner required | DECLARED |

`DECLARED` is not counted as PASS. These entries are outside the local PupilSpec owner.
