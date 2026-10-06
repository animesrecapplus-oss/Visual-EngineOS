# Test status — CMP-FACE-MOUTH — V1.81

## Focused V1.81

- `tests/components/face/mouth/test_v181_mouth_input_hardening.py`: 4 tests PASS.
- existing `test_mouth_contract.py`: 3 tests PASS.
- production mouth/overlap/style/face-calibration integration selection: 43 tests PASS.

## Structural

- source identity: PASS;
- database identity: PASS;
- dependency graph: PASS; 3 SCCs are pre-existing and unchanged;
- exact duplicate function groups: 0;
- truth validator: PASS after final manifest update;
- compileall: PASS.

## Full regression

The full matrix must be executed in deterministic batches. The final certification records exact collected/passed/skipped/failed counts.
The PostgreSQL integration skip remains environment-dependent when `VISUAL_ENGINE_POSTGRES_DSN` is absent.

## Visual

V1.81 valid front/+12°/-12° and visibility interaction SVG hashes match the V1.80 baseline exactly.
This is an invariance claim, not a visual-quality improvement claim.
