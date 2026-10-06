# Current status — V1.56

## V1.56 — HumanFace Ear production integration

A fresh read-only audit of certified V1.55 confirmed that `unresolved_domain_result()` still has no production consumer, so no speculative runtime extraction was made.

The next evidence-backed production family was `Ear`: V1.47 had already proved the first real overlap path, and V1.55 had made Mouth production-real. V1.56 adds the two existing HumanFace Ear children to the production geometry path.

### Production path

`build_human_face → ProductionRenderSession → resolution/cache → face.human_with_eyes_nose_mouth_ears → Ear geometry → camera transform → generic SVG`.

### Evidence

- targeted V1.56 ear + V1.55 compatibility + V1.47/V1.46/V1.45 production tests: 39 passed;
- complete deterministic test inventory: 128 test files / 1041 tests / 1040 passed / 1 expected PostgreSQL skip / 0 failed;
- compileall PASS;
- 186 production modules / 458 internal edges / 3 pre-existing SCCs / 0 new SCCs;
- exact duplicate function groups: 0;
- COLOR source files byte-identical to V1.55;
- database migrations unchanged from V1.55;
- real front/+12°/-12° outputs and left-ear hidden interaction manually inspected.

### Performance

Certified artifact `artifacts/current/v1.56/V1.56_BENCHMARK.json` records the fresh-process V1.56 warm production render median as 24,184,976 ns versus V1.55 28,495,920 ns, a measured -15.128% change. The earlier 26,022,936 ns prose value was a documentation error corrected during the V1.57 audit. No speculative optimization was introduced.

## Status

`CERTIFIED / EAR PRODUCTION INTEGRATED / GENERIC RENDERER ROLE / VISUAL QA PASS / FULL REGRESSION PASS / COLOR UNCHANGED / DATABASE UNCHANGED / PERFORMANCE MEASURED`
