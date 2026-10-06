# Test status — CMP-FACE-HAIR-COMPOSITE

Focused V1.57 tests: `tests/unit/test_v157_production_hair.py:1-124` — 10 tests PASS.
V1.56 compatibility tests: `tests/unit/test_v156_production_ear.py:1-144` — 8 tests PASS in focused run.

Visual QA: `tools/visual_qa_v157_production_hair.py:1-80` generated front/+12°/-12°,
visible and hidden evidence from the real production path.

Benchmark: `tools/benchmark_v157_production_hair.py:1-46`.

Full regression status is recorded only after the final deterministic suite completes;
this dossier does not promote an incomplete run to PASS.

Full V1.57 inventory: 129 test files / 1050 tests / 1049 passed / 1 expected PostgreSQL skip / 0 failed.
