# Test status — CMP-VBOOL-001

Final test inventory: 1150 tests collected (82 components + 5 integration + 1063 unit); 1149 passed and 1 expected PostgreSQL skip.

Focused final suites:

- `tests/components/runtime/visibility_boolean/test_v175_visibility_boolean_truth.py`
- `tests/unit/test_v13_visibility_kernel.py`
- `tests/unit/test_v13_visibility_attribution.py`
- `tests/unit/test_v147_production_visibility.py`
- `tests/unit/test_v13_consequences.py`

Focused result: 40 passed across the dedicated and affected visibility suites.

The complete deterministic regression was executed as explicit component/integration/unit batches because the monolithic runner exceeded the execution window; every batch passed. One expected PostgreSQL integration test remains skipped because no live PostgreSQL DSN was available. Final compileall passes.
