# Current status — V1.65

## V1.57 — HumanFace Hair production integration

Fresh V1.56 audit found no evidence to extract the unresolved domain-result seam. The existing HumanFace `Hair` child was the next bounded production family with a real consumer boundary. V1.57 therefore adds one closed Hair cap, one explicit Hair-inclusive composite and the minimal generic SVG role needed to paint it.

### Production path

`build_human_face → ProductionRenderSession → resolution/cache → face.human_with_eyes_nose_mouth_ears_hair → Hair geometry → camera transform → generic SVG`.

### Evidence

- 129 test files / 1050 tests / 1049 passed / 1 expected PostgreSQL skip / 0 failed across deterministic batches.
- compileall PASS.
- 188 production modules / 469 internal edges / 3 pre-existing SCCs / 0 new SCCs.
- exact duplicate function groups: 0.
- COLOR source files changed: 0.
- database migrations changed: 0.
- front/+12°/-12° and Hair visible/hidden production evidence generated and inspected.

### Performance

Fresh V1.57 warm render median: 26,043,919 ns. Certified V1.56 artifact reference: 24,184,976 ns. Measured change: +7.686%. No speculative optimization was introduced.

## Status

`CERTIFIED / HAIR PRODUCTION INTEGRATED / GENERIC RENDERER ROLE / VISUAL QA PASS / FULL DETERMINISTIC REGRESSION PASS / COLOR UNCHANGED / DATABASE UNCHANGED / PERFORMANCE MEASURED`

## V1.58 — Hair/Ear production occlusion

Fresh V1.57 audit proved a real Hair/Ear geometric overlap in the production face. The bounded relation is now resolved through the existing generic visibility/attribution kernel. Hair depth is authored at `1` and Ear at `0`, aligning semantic depth with the existing renderer paint order.

Evidence: left Ear coverage `0.0028187960`, right Ear coverage `0.0091032108`, both `DepthRelation.FRONT`; hidden Hair restores optical visibility to approximately `1.0` while preserving geometric overlap.

Focused V1.58: 6/6 PASS. Focused compatibility V1.47/V1.55/V1.56/V1.57/V1.58: 36/36 PASS. Visual QA PASS. Fresh warm median: `31,476,815.5 ns`; V1.57 certified reference `26,043,919 ns`; measured change `+20.8605%`. No speculative optimization introduced.

COLOR unchanged. Database schema unchanged. Generic visibility/attribution kernels unchanged.

## Status

`V1.58 / HAIR-EAR OCCLUSION / DEPTH CONTRACT / VISUAL QA PASS / FULL DETERMINISTIC REGRESSION PASS / CERTIFIED`

## V1.59 — Head/Ear production visibility

Fresh V1.58 audit found real Head/Ear overlap in the certified production face: left Ear coverage by the Head
`0.1554738957`, right `0.2184405039`. Both owners are authored at depth `0`; renderer paint order places Ear
before Head. V1.59 therefore uses explicit coplanar occlusion rather than changing depth semantics.

Implemented:
- canonical production target/occluder pair owner;
- Hair/Ear delegation with attribution preserved;
- Head/Ear visibility-only relation;
- generic visibility depth-result correction so coplanar results remain `COPLANAR`.

Focused V1.59 suite: 7 Head/Ear tests; V1.47/V1.55/V1.56/V1.57/V1.58/V1.59 compatibility matrix 43/43 PASS.
Full regression: 131 test files / 1064 tests / 1063 passed / 1 expected PostgreSQL skip / 0 failed. Compileall PASS;
191 production modules / 492 internal edges / 3 pre-existing SCCs / 0 new SCCs / 0 duplicates. Visual QA PASS.
Official V1.58-reference warm benchmark comparison is +54.5714%; same-process A/B incremental Head/Ear cost is +8.2758%.
These are measurements, not non-regression claims.

Status: `V1.59 / HEAD-EAR VISIBILITY / COPLANAR DEPTH CONTRACT / FOCUSED PASS / VISUAL QA PASS / FULL DETERMINISTIC REGRESSION PASS / CERTIFIED`

## V1.60 — Production face-overlap visibility extraction

Fresh V1.59 audit found an existing real production responsibility still embedded in `production_slice.py`: the Head→{Nose,Mouth}
visibility result contract and resolver. This was not a new consumer; it was an existing consumer boundary selected for a single-responsibility extraction.

Implemented `CMP-RUNTIME-PRODUCTION-FACE-OVERLAP-VISIBILITY` in
`src/visual_engine/runtime/production_face_overlap_visibility.py:17-111`. The existing owner-geometry extractor remains in
`production_slice.py:47-86` and is injected into the new owner, preventing duplication and dependency cycles.

Behavior identity evidence: certified V1.59 and V1.60 production SVG SHA-256 are identical; camera geometry digest,
geometry cache key, visibility coverage and causal attribution are identical. No renderer algorithm, COLOR, persistence,
database schema, cache owner or generic visibility algorithm changed.

Focused extraction suite: 5/5 PASS. Compatibility matrix V1.47/V1.55/V1.56/V1.57/V1.58/V1.59 plus V1.60 extraction: PASS.

Benchmark is measurement only: V1.59 warm median `32,774,582 ns`; V1.60 warm median measured `18,525,928 ns` in the certification run.
The large negative delta is environment-sensitive and is not promoted to a non-regression claim.

Status: `V1.60 / PRODUCTION FACE-OVERLAP VISIBILITY EXTRACTION / BEHAVIOR IDENTITY PASS / FULL DETERMINISTIC REGRESSION PASS / CERTIFIED`


## V1.61 — Production visual-style map extraction

Fresh V1.60 audit found one existing production responsibility still embedded in `ProductionRenderSession.render_face`: construction of the
renderer-facing style map from camera-space geometry owner metadata. This was an existing consumer boundary, not a new appearance consumer.

Implemented `CMP-RUNTIME-PRODUCTION-VISUAL-STYLES` in
`src/visual_engine/runtime/production_visual_styles.py:18-66`. The root `ResolvedVisualContract` is injected from the session's already-computed
`ResolvedComponent`; non-root owners delegate to the canonical `resolve_component` path. This prevents a second root resolution and preserves
resolution-cache/fingerprint behavior.

Behavior identity evidence: V1.60 and V1.61 production SVG SHA-256, camera-geometry digest, geometry cache key, visibility/attribution values
and resolution-cache statistics are identical for the certified comparison request. Front, +12°, -12° and hidden-root visual cases also match
V1.60 SVG bytes exactly.

Focused V1.61: 7/7 PASS. Compatibility V1.47/V1.55/V1.56/V1.57/V1.58/V1.59/V1.60/V1.61: PASS. Full inventory: 133 test files /
1076 collected tests / 1075 PASS / 1 expected PostgreSQL skip / 0 FAIL, executed in deterministic isolated batches; the long batches were
split further where the execution window was insufficient, without treating a timeout as a PASS. Compileall PASS.

Dependency audit: 193 production modules / 501 internal edges / 3 pre-existing SCCs / 0 new SCCs / 0 exact duplicate function groups.
COLOR semantic change: false. Direct persistence consumer: false. New cache owner: false.

Benchmark comparison is measurement only. Five V1.61 warm medians were measured against the same V1.60 request; the resulting delta is environment-sensitive and is not promoted to a performance non-regression claim.

Status: `V1.61 / PRODUCTION VISUAL-STYLE MAP EXTRACTION / BEHAVIOR IDENTITY PASS / FULL DETERMINISTIC REGRESSION PASS / VISUAL IDENTITY PASS / CERTIFIED`

## V1.62 — Production owner-geometry extraction

Fresh V1.61 audit found one existing shared production responsibility still embedded in `production_slice.py`: selecting one camera-space
geometry owner, rebasing its path indices and reading its authored depth layer for the real face-overlap, Hair/Ear and Head/Ear consumers.
This is an existing consumer boundary, not a newly invented geometry consumer.

Implemented `CMP-RUNTIME-PRODUCTION-OWNER-GEOMETRY` in
`src/visual_engine/runtime/production_owner_geometry.py:8-67`. The former private helper is removed from `production_slice.py`; all three
production interaction paths use the canonical callable. The public runtime export points to the new owner.

Focused V1.62: 6/6 PASS; focused compatibility matrix V1.47/V1.55/V1.56/V1.57/V1.58/V1.59/V1.60/V1.61/V1.62: 55/55 PASS. Full regression: 134 test files / 1082 collected / 1081 PASS / 1 expected PostgreSQL skip / 0 FAIL. Compileall PASS.
Dependency graph: 194 modules / 503 edges / 3 pre-existing SCCs / 0 new SCCs / 0 exact duplicate function groups. No COLOR semantic change, database migration, persistence consumer, cache owner or fingerprint algorithm changed.

Behavior identity evidence: real owner geometry hashes/depths, SVG bytes and resolution-cache statistics match certified V1.61. Visual QA front,
+12°, -12°, visible-root and hidden-root cases are byte-identical to V1.61.

Benchmark is measurement only: five-run warm median V1.61 `17,286,877 ns`; V1.62 `17,467,504.5 ns`; measured change `+1.0449%`.

Status: `V1.62 / PRODUCTION OWNER-GEOMETRY EXTRACTION / BEHAVIOR IDENTITY PASS / VISUAL IDENTITY PASS / CERTIFIED`


## V1.63 — Production Hair/Ear relation orchestration extraction

Fresh V1.62 audit found one existing production orchestration responsibility still embedded in `ProductionRenderSession.render_face`:
resolving the real Hair → left/right Ear relations after camera geometry and renderer-facing styles were already resolved. This is an
existing consumer boundary, not a newly invented relation.

Implemented `CMP-RUNTIME-PRODUCTION-HAIR-EAR-RELATIONS` in
`src/visual_engine/runtime/production_hair_ear_relations.py`. The one-pair `production_hair_ear_occlusion` owner, canonical
owner-geometry extractor and Head/Ear/face-overlap responsibilities remain separate.

Focused V1.63 and compatibility evidence are recorded under `artifacts/current/v1.63/`. Full regression, dependency/cycle/duplicate audit,
compileall, visual identity and artifact cleanup are certification gates. PostgreSQL remains skipped when `VISUAL_ENGINE_POSTGRES_DSN` is absent.

Status: `V1.63 / PRODUCTION HAIR-EAR RELATION ORCHESTRATION EXTRACTION / BEHAVIOR IDENTITY PASS / VISUAL IDENTITY PASS / CERTIFIED`
