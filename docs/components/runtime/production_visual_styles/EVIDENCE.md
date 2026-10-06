# Evidence

`EVD-PVS-001`: focused V1.61 suite: 7/7 PASS.
`EVD-PVS-002`: compatibility matrix V1.47/V1.55/V1.56/V1.57/V1.58/V1.59/V1.60/V1.61 PASS.
`EVD-PVS-003`: V1.60 and V1.61 SVG SHA-256 are identical for front, +12°, -12°, visible-root and hidden-root requests.
`EVD-PVS-004`: V1.60 and V1.61 camera-geometry digest, GeometryCacheKey, visibility coverage/visible and attribution are identical.
`EVD-PVS-005`: V1.60 and V1.61 resolution-cache statistics are identical for the certified comparison request.
`EVD-PVS-006`: five-run warm medians: V1.60 `19,840,437 ns`; V1.61 `20,607,962 ns`; measured `+3.8685%`.
This is an environment-sensitive measurement only; it is not a performance non-regression claim.
`EVD-PVS-007`: dependency audit reports 193 modules / 501 internal edges / 3 pre-existing SCCs / 0 new SCCs / 0 duplicate function groups.
`EVD-PVS-008`: only `artifacts/current/v1.61/` remains; pycache/pyc/pyo/pytest cache are purged before release packaging.
