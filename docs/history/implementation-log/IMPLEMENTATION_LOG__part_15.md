# Implementation log — V1.54

## 2026-10-01

### CMP-DOMAIN-INPUT-FACTORY

V1.54 started from the certified V1.53 checkpoint. The fresh audit identified the canonical `build_domain_resolution_input` factory as the only remaining `domain_resolution` responsibility with real independent production consumers.

The factory was moved to `src/visual_engine/runtime/domain_input_factory.py` lines 1–64. BASE, COLOR and MATERIAL now import the canonical owner directly. `domain_resolution.py:42` preserves the historical symbol identity.

A hostile API gap was corrected: non-`DomainDependency` sequence members are rejected before sorting. No valid input semantics, digest ownership, cache identity, persistence behavior or COLOR algorithm changed.

Dedicated truth dossier: `docs/components/runtime/domain_input_factory/`.

Evidence: 125 test files / 1023 tests / 1022 passed / 1 expected PostgreSQL skip / 0 failed; compileall PASS; 181 modules / 435 edges / 3 pre-existing SCCs / 0 exact duplicates.

Visual QA is `NOT_APPLICABLE` because the selected seam contains no rendering responsibility. Only `artifacts/current/v1.54/` remains as generated current evidence.

## V1.58 — 2026-10-01

Implemented `CMP-FACE-HAIR-DEPTH` and `CMP-PROD-HAIR-EAR-OCCLUSION` after fresh V1.57 audit.

The audit measured real Hair/Ear intersection before implementation. The first adapter attempt exposed a path-vs-area contract mismatch and was corrected to use `generic_geometry_region_map`; coplanar Hair/Ear depth was then corrected to `1/0` so semantic visibility agrees with the existing paint order.

Focused tests, visual QA and benchmark were rerun after correction. Final evidence records 130 test files / 1056 tests / 1055 passed / 1 PostgreSQL skip / 0 failed, compileall PASS, 189 modules / 477 edges / 3 pre-existing SCCs / 0 new SCCs, artifact purge and ZIP integrity PASS. V1.58 is certified.

## V1.59 — 2026-10-01

Fresh V1.58 audit measured a second production interaction: HumanFace head → Ear. Left/right Ear coverage by
Head is `15.5473896%` / `21.8440504%`. Renderer paint order puts Ear before Head while both remain at depth `0`.

Implemented `CMP-RUNTIME-PRODUCTION-PAIR-OCCLUSION`, `CMP-PROD-HEAD-EAR-OCCLUSION` and
`CMP-RUNTIME-VISIBILITY-DEPTH-RELATION`. Hair/Ear delegates to the canonical pair owner without changing
its public or attribution contract. Head/Ear explicitly enables coplanar occlusion and deliberately does not
claim attribution because no real downstream consumer exists.

The first Head/Ear implementation computed unnecessary attribution and was rejected after benchmark/profile.
The final bounded implementation keeps attribution disabled for Head/Ear. A generic visibility contract bug
was exposed and corrected: coplanar region results now remain `COPLANAR` rather than `FRONT`.

Certification evidence is generated under `artifacts/current/v1.59/`; final status is not inferred from focused tests.

## V1.60 — 2026-10-01

Fresh V1.59 audit selected one existing responsibility rather than inventing a new production interaction: the Head→Nose/Mouth
visibility result and resolver embedded in `production_slice.py`.

Implemented `CMP-RUNTIME-PRODUCTION-FACE-OVERLAP-VISIBILITY` at
`src/visual_engine/runtime/production_face_overlap_visibility.py:17-111`. The owner-geometry extractor remains at
`production_slice.py:47-86` and is injected explicitly, so no geometry logic is duplicated and no dependency cycle is introduced.

The existing production consumer now calls the canonical owner at `production_slice.py:193-197`. The existing
`ProductionVisibilityResolution` import path remains available through `runtime.__init__`.

Focused extraction tests: 5/5 PASS. Compatibility matrix V1.47/V1.55/V1.56/V1.57/V1.58/V1.59 plus V1.60 extraction: PASS.
Certified V1.59 and V1.60 SVG SHA-256, camera-geometry digest, geometry cache key, visibility and attribution are identical.
No COLOR, database, cache owner, renderer algorithm or generic visibility algorithm changed.


## V1.61 — Production visual-style map extraction

Verified from the certified V1.60 checkpoint. A fresh read-only audit identified an existing production style-map construction inside
`ProductionRenderSession.render_face`; no new consumer was invented.

Implemented `CMP-RUNTIME-PRODUCTION-VISUAL-STYLES` at
`src/visual_engine/runtime/production_visual_styles.py:18-66`, consumed by
`production_slice.py:173-178`. The root visual is injected from the already-computed `ResolvedComponent` to preserve one resolution/cache lookup.

Focused suite: 7/7 PASS. Full deterministic inventory: 133 files / 1076 collected tests / 1075 PASS / 1 expected PostgreSQL skip / 0 FAIL.
Compileall PASS. Dependency graph: 193 modules / 501 edges / 3 pre-existing SCCs / 0 new SCCs / 0 duplicates.
Behavior identity and visual identity versus V1.60 are exact for the tested production cases.

No COLOR semantic change, database migration, persistence consumer or new cache owner. Benchmark is measurement only.
Status: CERTIFIED.

## V1.62 — Production owner-geometry extraction

Fresh V1.61 audit found an existing shared production responsibility in `production_slice.py`: `_owner_geometry` selected one camera-space
owner, rebased its selected path indices and returned the authored depth used by three real production interaction paths.

Implemented `CMP-RUNTIME-PRODUCTION-OWNER-GEOMETRY` at
`src/visual_engine/runtime/production_owner_geometry.py:8-67`. The old private helper was removed; the Head→Nose/Mouth,
Hair/Ear and Head/Ear paths now consume the canonical extractor. The runtime public export was updated.

Focused V1.62: 6/6 PASS. Real owner geometry hashes/depths, SVG SHA-256 values and resolution-cache statistics are identical to certified V1.61.
Visual QA was generated from the production path and inspected. No COLOR, database, persistence, cache-lifetime or fingerprint semantic change.

Five-run warm benchmark: V1.61 median `17,286,877 ns`; V1.62 median `17,467,504.5 ns`; measured delta `+1.0449%`, recorded as environment-sensitive
measurement only. Final certification includes deterministic full regression, compileall, dependency/cycle/duplicate audit, truth validation,
artifact purge and ZIP integrity.

## V1.64 — Production Head/Ear relation orchestration extraction

Fresh V1.63 audit selected the existing two-Ear Head/Ear orchestration embedded in `ProductionRenderSession.render_face`; no new consumer was invented.

Implemented `CMP-RUNTIME-PRODUCTION-HEAD-EAR-RELATIONS` at
`src/visual_engine/runtime/production_head_ear_relations.py:18-65`, consumed by
`production_slice.py:155-157`. The canonical Head/Ear leaf, owner-geometry extractor and resolved Head style remain separate owners.

Focused V1.64: 5/5 PASS. Exact checkpoint A/B against extracted certified V1.63 used front, +12°, -12°, Hair-hidden and Head-hidden cases;
all SVG hashes, camera geometry hashes, relation evidence and resolution-cache statistics matched. Visual QA was generated and inspected.

Benchmark: V1.63 warm median `33,615,254 ns`; V1.64 `31,963,200 ns`; measured change `-4.9146%`, recorded as environment-sensitive
measurement only. No speculative optimization introduced.

No COLOR semantic change, database migration, persistence consumer, new cache owner or fingerprint algorithm change. Final certification
requires deterministic full regression, compileall, dependency/cycle/duplicate audit, truth validation, artifact purge and ZIP integrity.


## V1.65 — Production face-overlap relation orchestration extraction

Fresh V1.64 audit selected the remaining generator-specific Head→Nose/Mouth orchestration in `ProductionRenderSession.render_face`.
No new semantic visibility consumer was invented.

Implemented `CMP-RUNTIME-PRODUCTION-FACE-OVERLAP-RELATIONS` at
`src/visual_engine/runtime/production_face_overlap_relations.py:26-61`. The canonical
`production_face_overlap_visibility` resolver, owner geometry extractor and generic visibility/attribution kernels remain owners of their
existing responsibilities.

A hostile owner-geometry test initially exposed an unchecked downstream type boundary; the new adapter was corrected to validate
`GeometryContract` and finite numeric depth before delegation. A visual QA assertion was also corrected after it referenced a non-existent
semantic-region area attribute. Both affected gates were rerun.

Exact V1.64→V1.65 behavior identity passed for five production cases; focused V1.65 passed 9/9. Benchmark was measurement only.
No COLOR, database, persistence, cache owner or fingerprint algorithm change.

## V1.66 — Production geometry service lifecycle extraction

Fresh V1.65 audit selected the existing registry/service construction and teardown responsibility inside `ProductionRenderSession`.
Implemented `CMP-RUNTIME-PRODUCTION-GEOMETRY-SERVICE-RESOURCES` at
`src/visual_engine/runtime/production_geometry_service_resources.py:11-39`.

The first broader resource extraction moved cache construction and was rejected by two historical cache-owner tests. The impact analysis
was reopened and cache ownership returned to `production_slice.py`; the final owner only manages the production geometry registry and
`CachedGeometryGenerator` references.

Focused 4/4 PASS. Final deterministic regression: 138 files / 1105 collected / 1104 PASS / 1 expected PostgreSQL skip / 0 FAIL.
Exact five-case behavior/visual identity versus fresh V1.65 execution passed. No COLOR/database/persistence/cache-policy/fingerprint change.
