# CMP-EYE-LASH — adversarial matrix

| ID | Case | Expected | V1.85 |
|---|---|---|---|
| ADV-LASH-001 | NaN density/length/thickness/curvature | reject | PASS |
| ADV-LASH-002 | +/-inf real fields | reject | PASS |
| ADV-LASH-003 | bool count | reject | PASS |
| ADV-LASH-004 | fractional count | reject | PASS |
| ADV-LASH-005 | numeric string | reject | PASS |
| ADV-LASH-006 | negative bounded/non-negative fields | reject | PASS |
| ADV-LASH-007 | zero valid count/length/thickness where existing contract allows | accept | PASS |
| ADV-LASH-008 | valid authored presets | accept | PASS |
| ADV-LASH-009 | lower-lash NaN/inf/count cases | reject | PASS |
| ADV-LASH-010 | invalid style/form | reject | PASS |
| ADV-LASH-011 | coercive enabled values | reject | PASS |
| ADV-LASH-012 | numeric strings in real fields | reject | PASS |

## Interaction cases

- Closed/covered eye suppresses lash emission: existing system contract, regression tested.
- Terminal exclusion remains renderer-owned and unchanged.
- Visibility remains downstream and unchanged.
- Cache/fingerprint semantics are unchanged by this local validation brick.
