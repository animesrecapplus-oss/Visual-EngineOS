# V1.64 pre-change audit — READ-ONLY evidence

Baseline: certified V1.63 checkpoint.

## VERIFY
- V1.63 status/roadmap read; V1.64 rule requires a fresh owner/consumer/contracts/relations/cache/fingerprint/persistence/visual audit.
- Architecture immune system read; one canonical owner and no speculative extraction.
- V1.63 artifact policy read; repository contains only `artifacts/current/v1.63/` and no Python caches.

## ARCHITECT
Candidate responsibility found in the real production path: `ProductionRenderSession.render_face` still directly orchestrates the two Head/Ear relations after canonical geometry and style resolution.
- Real consumer: `src/visual_engine/runtime/production_face_render.py:92-94`.
- Existing semantic leaf owner: `src/visual_engine/runtime/production_head_ear_occlusion.py:59-78`.
- Existing geometry owner: `src/visual_engine/runtime/production_owner_geometry.py:8-67`.
- Existing style owner: `src/visual_engine/runtime/production_visual_styles.py:18-66`.
- Parent/lifecycle owner: `ProductionRenderSession` in `production_render_session.py:18-118`.
- Siblings: face-overlap visibility and Hair/Ear relation orchestration.

Responsibility proposed for exactly one new module: orchestrate the two existing Head/Ear leaf calls in stable left/right order, forwarding the already resolved Head style and canonical owner-geometry callable.

Explicit non-responsibility: Head/Ear visibility algorithm, geometry generation, camera transform, style resolution, attribution, renderer, COLOR, cache lifetime, fingerprints, persistence and database.

## IMPACT
- Source: one new orchestration module; one production call-site import/replacement; one public runtime export; no leaf algorithm changes.
- Consumers: only the existing production session consumer plus public API for the new orchestrator; leaf public API remains unchanged.
- Parent/children/siblings: session remains lifecycle owner; Head/Ear leaf remains semantic owner; face-overlap and Hair/Ear remain separate.
- Contracts/invariants: preserve two-result order `(left_ear, right_ear)`, one Head geometry extraction, exact Head effective visibility/transmission forwarding, missing-ear fail-closed behavior.
- Cache/fingerprint: no new resolution; use existing style and geometry inputs; no cache owner/fingerprint change.
- Persistence/database: no SQL/schema/migration/consumer.
- COLOR: no change; no downstream COLOR consumer.
- Determinism: preserve historical Ear order and tuple construction.
- Visual: exact V1.63 SVG/result identity is a hard release gate.
- Behavior that must remain identical: previous generators return empty Head/Ear tuple; Hair-inclusive generator returns two relations with same coverage/visible/depth/IDs/regions/attribution; renderer paint order unchanged.

## STOP CONDITIONS CHECK
No ambiguous ownership, no unknown required consumer, no contradictory contract, no planned new cycle, and visual identity is testable by exact SVG bytes.

## Reopened impact during validation

The first identity probe compared a different case sequence and therefore produced a cache-stat mismatch; no production behavior change was inferred. The certified V1.63 checkpoint was extracted separately and both versions were rerun with the exact same five-case sequence. All SVG/result/cache evidence matched.

The first full-regression pass also exposed two governance-gate conditions: superseded current artifacts and two >150-line governance files. Both were corrected before the affected test groups were rerun.
