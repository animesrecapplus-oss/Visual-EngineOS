# Current status — V1.55

## V1.55 — HumanFace Mouth production integration

V1.55 starts from certified V1.54. A bounded audit confirmed that `runtime.domain_resolution.unresolved_domain_result()`
still has no production consumer; it was not extracted speculatively.

The active production frontier was instead advanced through the already-proven V1.47 head/nose overlap: the existing
`HumanFace/mouth` child is now a real generated/rendered component.

### Production path

`build_human_face → ProductionRenderSession → resolution/cache → face.human_with_eyes_nose_mouth →
Mouth geometry → camera transform → generic SVG → explicit head/{nose,mouth} visibility/attribution`.

### Evidence

- 127 test files / 1032 tests / 1031 passed / 1 expected PostgreSQL skip / 0 failed.
- compileall PASS.
- 184 production modules / 447 internal edges / 3 pre-existing SCCs / 0 new SCCs.
- exact duplicate groups: 0.
- COLOR runtime unchanged byte-for-byte from V1.54.
- database migrations unchanged from V1.54.
- real front/+12°/-12° and mouth visible/hidden outputs manually inspected.

### Performance

Fresh-process measurement: multi-occluder visibility 7,049,885.5 ns; nose-only 5,749,075.5 ns;
warm production render 28,495,920.0 ns. The increase versus V1.47 is recorded rather than hidden.
No speculative cache was added.

## Status

`CERTIFIED / MOUTH PRODUCTION INTEGRATED / MULTI-OCCLUDER PROOF / VISUAL QA PASS /
FULL REGRESSION PASS / COLOR UNCHANGED / DATABASE UNCHANGED / PERFORMANCE MEASURED`
