# Domain-resolution test status — V1.53

## Focused

- V1.53 input-contract ownership/API tests: PASS.
- Hostile constructor/type tests: PASS.
- Existing domain/BASE/COLOR/MATERIAL tests: PASS.
- V1.52 result-contract tests: PASS.
- Production/cache/visibility integration set: PASS.

## Full matrix

- 124 test files.
- 1016 tests collected.
- 1015 passed.
- 1 expected PostgreSQL skip (`VISUAL_ENGINE_POSTGRES_DSN` absent).
- 0 failed.

The deterministic inventory was executed in completed batches and isolated final ocular files after larger batches exceeded
the execution window. The timeout itself was never counted as PASS; every one of the 124 files was subsequently executed
to completion on the final source state.

## Structural

- component truth gate: PASS.
- compileall: PASS.
- 180 production modules / 428 internal edges: PASS.
- 3 SCCs, all pre-existing: PASS.
- exact duplicate groups: 0.
- persistence direct consumer: false.
- COLOR semantic change: false.

## Performance

Five fresh-process runs compare the V1.53 input owner against the certified V1.52 facade path. Median-of-medians:
build 4868.0 ns → 5128.0 ns (+5.341%); input digest 15693.0 ns → 15408.0 ns (-1.816%). This is recorded as a measured
correctness/modularization cost, not as an optimization claim.

## Visual

`NOT_APPLICABLE`: the selected input contract contains no geometry or renderer operation. Existing production-render
regression coverage remains the evidence boundary; no V1.53 PNG/SVG is claimed.
