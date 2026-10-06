# Adversarial test matrix — CMP-EYE-GAZE

| ID | Case | Expected |
|---|---|---|
| `ADV-GAZE-001` | bool numeric fields | reject |
| `ADV-GAZE-002` | numeric strings | reject |
| `ADV-GAZE-003` | NaN / ±inf | reject |
| `ADV-GAZE-004` | huge integer | reject with domain error |
| `ADV-GAZE-005` | target bool/string element | reject |
| `ADV-GAZE-006` | target NaN/±inf | reject |
| `ADV-GAZE-007` | huge target integer | reject with domain error |
| `ADV-GAZE-008` | mutable/non-pair target | reject |
| `ADV-GAZE-009` | invalid direction | reject |
| `ADV-GAZE-010` | negative strength/amplitude | reject |

Interaction checks additionally cover target-vector arithmetic, transform use, binocular pair construction,
immutability and valid boundary values.
