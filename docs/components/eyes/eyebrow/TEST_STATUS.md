# V1.87 — test status — CMP-EYE-EYEBROW

- `TST-EYEBROW-001`: focused owner suite `tests/components/face/eyes/eyebrow/test_v187_eyebrow_input_hardening.py:1-75` — 72/72 PASS.
- `ADV-EYEBROW-001..010`: hostile matrix in `ADVERSARIAL_TEST_MATRIX.md` — PASS.
- Existing eyebrow-related integration/regression tests — PASS.
- `tests/components`: 359 tests — PASS.
- `tests/integration`: 5 tests — PASS.
- `tests/unit`: 1079 tests — PASS, executed in five chunks because the monolithic invocation exceeded the available
  execution window; chunks 1–5 all completed with return code 0.
- Full collected suite across `tests/`: 1443 tests.
- One PostgreSQL integration test is expected to SKIP when `VISUAL_ENGINE_POSTGRES_DSN` is absent; no test failure.
- `compileall -q src tests tools`: PASS.

No test is treated as proof of complete correctness in isolation.
