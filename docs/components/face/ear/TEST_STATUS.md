# Test status — CMP-FACE-EAR

## Focused V1.80

- V1.80 Ear hardening tests: PASS.
- Ear production, head-ear occlusion and hair-ear relation suites: PASS.
- Valid geometry contract and public registry behavior: PASS.

## Final V1.80 matrix

- 151 test files.
- 1180 tests collected.
- 1179 passed, 1 expected PostgreSQL skip, 0 failed.
- Final totals are recorded in `artifacts/current/v1.80/V1.80_CERTIFICATION.json`.
- Expected PostgreSQL skip remains the only environment-dependent skip when `VISUAL_ENGINE_POSTGRES_DSN` is absent.
- 0 failed at certification.

Structural gates: compileall PASS; no new import SCC; no exact duplicate function group introduced; DB tree unchanged.
