# CMP-EYE-EYELID — adversarial matrix

| ID | Attack | Expected | V1.86 |
|---|---|---|---|
| `ADV-EYELID-001` | NaN on each real field | reject | PASS |
| `ADV-EYELID-002` | +inf on each real field | reject | PASS |
| `ADV-EYELID-003` | -inf on each real field | reject | PASS |
| `ADV-EYELID-004` | bool in real field | reject | PASS |
| `ADV-EYELID-005` | numeric string in real field | reject | PASS |
| `ADV-EYELID-006` | int/string/None in bool field | reject | PASS |
| `ADV-EYELID-007` | negative/out-of-range authored values | reject | PASS |
| `ADV-EYELID-008` | exact valid boundaries | accept | PASS |
| `ADV-EYELID-009` | invalid colors | reject | PASS |
| `ADV-EYELID-010` | frozen mutation | reject | PASS |
| `ADV-EYELID-011` | extremely large integer | reject without leaked overflow | PASS |

Property-based testing was considered but the baseline environment has no Hypothesis dependency. Deterministic
parameterized hostile coverage was used instead; no dependency was added solely for this brick.
