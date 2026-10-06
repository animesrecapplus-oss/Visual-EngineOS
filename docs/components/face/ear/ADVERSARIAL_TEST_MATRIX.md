# Adversarial matrix — CMP-FACE-EAR

| ID | Attack | Expected | Evidence |
|---|---|---|---|
| `ADV-FE-001` | NaN/∞ malformed width/height | rejected by leaf generator | `TST-FE-180-002` |
| `ADV-FE-002` | negative/zero dimensions | rejected by generator | existing V1.56 test |
| `ADV-FE-003` | custom inputs | `TypeError` | existing V1.56 test |
| `ADV-FE-004` | malformed parameter object | typed failure, no silent coercion | `TST-FE-180-003` |
| `ADV-FE-005` | non-finite geometry metadata | `GeometryContract` rejects | existing contract suite |
| `ADV-FE-006` | duplicate ear IDs | generic `Component.add_child` rejects | existing composite suite |
| `ADV-FE-007` | missing/extra ears | composite rejects cardinality | existing composite suite |
| `ADV-FE-008` | cache stale after parameter mutation | geometry identity changes | existing V1.56 test |
| `ADV-FE-009` | hidden ear | renderer emits no visible ear paint | existing V1.56 test |
| `ADV-FE-010` | deterministic repeated render | identical SVG/fingerprint | production regression |
| `ADV-FE-011` | boolean/string dimensions | rejected before geometry math | `TST-FE-180-003` |
| `ADV-FE-012` | positive subnormal dimension | rejected before degenerate path | `TST-FE-180-004` |
