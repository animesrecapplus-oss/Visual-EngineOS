# Test status — CMP-EYE-HIGHLIGHT V1.88

TST-HIGHLIGHT-001 — focused adversarial suite: **60 PASS / 0 FAIL**.

Coverage includes all numeric fields, NaN, ±∞, bools, numeric strings, huge integer overflow, closed shape vocabulary,
unhashable/opaque shape values, existing ranges, valid boundaries, color retention and immutability.

Consumer regression after final source state:

- `tests/components`: 416 PASS / 0 FAIL.
- `tests/integration`: 4 PASS / 1 expected PostgreSQL SKIP / 0 FAIL.
- `tests/unit`: 1079 PASS / 0 FAIL, executed in five deterministic chunks because a monolithic invocation exceeds the
  available execution window.
- Total collected: 1500; PASS 1499; expected SKIP 1; FAIL 0.
- `python -m compileall -q src tests tools`: PASS.

Property-based testing: NOT_AVAILABLE; Hypothesis is not installed. Differential rendering and deterministic adversarial
parameterization are available and used.
