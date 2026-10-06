# Decisions — CMP-EYE-HIGHLIGHT

- `DEC-HIGHLIGHT-001`: select Highlight after the V1.88 horizontal audit because a real executable owner, real consumers
  and reproducible local defects are verified. Recent V1.82/V1.84/V1.85/V1.86/V1.87 hardened owners remain deferred.
- `DEC-HIGHLIGHT-002`: keep validation local to `highlights/spec.py`; changing shared `_finite` would widen the impact surface.
- `DEC-HIGHLIGHT-003`: close the runtime shape vocabulary because the renderer has four explicit branches and otherwise
  routes every unknown value into the streak/rect fallback branch.
- `DEC-HIGHLIGHT-004`: use strict `Real`/non-bool finite validation with overflow/type failure handling, without coercion.
- `DEC-HIGHLIGHT-005`: do not add placement limits, cache fields, COLOR logic, persistence or renderer changes.

- `DEC-HIGHLIGHT-006`: local validation is preferred over shared `_finite` modification because the defect is specific to
  the ReflectionMark owner and shared coercive behavior has unrelated consumers.
- `DEC-HIGHLIGHT-007`: tuple membership is used for shape validation so unhashable malformed values fail closed with a
  domain `ValueError` instead of leaking a container `TypeError`.
- `DEC-HIGHLIGHT-008`: no renderer fallback was removed; the owner now prevents invalid values from reaching that branch.
