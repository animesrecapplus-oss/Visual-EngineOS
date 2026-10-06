# Evidence

`EVD-GSR-001`: certified V1.65 checkpoint verified by SHA-256 before extraction.

`EVD-GSR-002`: focused component tests: 4/4 PASS.

`EVD-GSR-003`: final deterministic repository regression: 138 test files / 1105 collected / 1104 PASS /
1 expected PostgreSQL skip / 0 FAIL; all files were executed in fresh pytest processes in deterministic batches.

`EVD-GSR-004`: dependency graph: 198 modules / 522 internal edges / 3 pre-existing SCCs / 0 new SCCs /
0 exact duplicate function groups.

`EVD-GSR-005`: exact V1.65→V1.66 five-case SVG, camera geometry, visibility, geometry-cache and resolution-cache identity.

`EVD-GSR-006`: visual QA board generated from the real production path and inspected for front, ±12°, visible and hidden cases.

`EVD-GSR-007`: benchmark comparison uses 3 fresh processes × 12 samples per version; measured change is recorded as environment-sensitive only.

`EVD-GSR-008`: compileall PASS and final artifact policy/ZIP integrity PASS after cleanup.
