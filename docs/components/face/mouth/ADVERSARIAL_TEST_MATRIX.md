# Hostile matrix — CMP-FACE-MOUTH

| ID | Attack | Expected boundary | Evidence |
|---|---|---|---|
| `ADV-MOUTH-001` | custom generator input | reject | existing contract test |
| `ADV-MOUTH-002` | zero width | reject | Parameter + V1.81 boundary test |
| `ADV-MOUTH-003` | negative width | reject | V1.81 boundary test |
| `ADV-MOUTH-004` | NaN / ±∞ bypassed width | reject before geometry | V1.81 boundary test |
| `ADV-MOUTH-005` | bool bypassed width | reject, no coercion | V1.81 boundary test |
| `ADV-MOUTH-006` | string numeric width | reject, no coercion | V1.81 boundary test |
| `ADV-MOUTH-007` | positive subnormal width | reject zero-radius result | V1.81 boundary test |
| `ADV-MOUTH-008` | missing Mouth child | reject composite topology | production test |
| `ADV-MOUTH-009` | duplicate Mouth | reject cardinality | composite dependency gate |
| `ADV-MOUTH-010` | target used as occluder | reject visibility result | production visibility invariant |
| `ADV-MOUTH-011` | stale cache after width mutation | new geometry key | V1.55 production test |
| `ADV-MOUTH-012` | dependency cycle | existing generation cycle guard | full regression |
| `ADV-MOUTH-013` | persistence unsupported value | generic payload guards | persistence regression |
| `ADV-MOUTH-014` | valid geometry visual regression | SVG identity preserved | V1.81 visual board |
| `ADV-MOUTH-015` | catastrophic hot-path slowdown | measure before optimization | V1.81 benchmark |

`DECLARED` or `BLOCKED` is not counted as PASS. Live PostgreSQL remains environment-dependent and is not promoted from skip.
