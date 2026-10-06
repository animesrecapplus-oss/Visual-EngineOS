# Adversarial matrix — CMP-PCOV-001

| ID | Attack | Expected / evidence |
|---|---|---|
| `ADV-PCOV-001` | NaN target fraction | reject; dedicated truth test |
| `ADV-PCOV-002` | ∞ target fraction | reject; dedicated truth test |
| `ADV-PCOV-003` | zero/invalid tolerance | reject |
| `ADV-PCOV-004` | too few iterations | reject |
| `ADV-PCOV-005` | wrong intent type | reject before geometry work |
| `ADV-PCOV-006` | non-finite anchor | reject before Shapely |
| `ADV-PCOV-007` | outside source/target anchor | reject |
| `ADV-PCOV-008` | unreachable coverage / extreme offset | explicit failure |
| `ADV-PCOV-009` | zero coverage | deterministic `1e-9` scale, zero iterations |
| `ADV-PCOV-010` | boundary anchor | accepted when contained |
| `ADV-PCOV-011` | public identity / frozen mutation | single owner and immutable contract |
| `ADV-PCOV-012` | dependency cycle / duplicate owner | graph + exact duplicate audits |
| `ADV-PCOV-013` | visual regression | production render hashes identical |
| `ADV-PCOV-014` | performance regression | fresh-process benchmark compared with V1.73 |
