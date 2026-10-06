# Test status — CMP-RUNTIME-PLACEMENT-CONTRACT

- `TST-PLAC-001`: focused owner/hostile truth suite — 4 passed.
- `TST-PLAC-002`: affected placement/relation/constraint/visibility suites — 27 passed.
- `TST-PLAC-003`: complete deterministic regression — 1158 collected; 1157 passed; 1 expected PostgreSQL skip; 0 failed.

Focused truth suite: 4 passed.

Affected placement/relation/constraint/visibility suites: 27 passed.

Full regression: 1158 collected; 1157 passed; 1 expected PostgreSQL skip; 0 failed.

Compileall: PASS.
Dependency graph: 209 modules / 698 direct edges; 0 new SCC; no new exact duplicate group.
Benchmark: baseline median 4095.425 ns; current median 4092.150 ns; delta -0.080%.
Visual QA: four production cases; SVG/camera hashes identical to V1.76.
Behavior identity: baseline/current placement solution output identical.
Truth and exact-line-range gates: PASS.
