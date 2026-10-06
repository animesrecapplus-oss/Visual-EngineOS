# Pre-change impact audit — V1.71

`CMP-RUNTIME-PRODUCTION-RENDER-SESSION`.

## VERIFY

Starting checkpoint: certified V1.70. Read current status, roadmap, architecture contract/principles, V1.70 decisions, protocol, artifact policy, and the V1.70 production-result truth dossier. SHA-256 of the V1.70 checkpoint ZIP was independently verified. The workspace was clean after removing superseded current artifacts before V1.71 implementation.

## ARCHITECT

Fresh audit first re-tested `resolve_component_contract`; static compatibility ownership creates a new cycle, so that candidate remains rejected. The selected responsibility is the existing 118-line `ProductionRenderSession` class in `production_slice.py`.

Owner after extraction: `src/visual_engine/runtime/production_render_session.py:18-118`.
Parent: production runtime public boundary. Children: none as semantic micro-components. Siblings: request orchestration, result contract, geometry resources, styles, relations and occlusion owners.

Responsibility: session lifetime, graph freshness, cache ownership, resource teardown and request delegation.
Non-responsibility: request semantics, resolution, geometry, renderer, visibility/occlusion, result definition, COLOR, fingerprinting, persistence.

## IMPACT

- Files: new session owner, compatibility facade, public runtime import, affected historical ownership tests, truth dossiers/manifests and governance evidence.
- Consumers: public runtime, compatibility facade, session integration tests and the real production path entered through the session.
- Parent/siblings: parent remains production public boundary; `production_face_render` remains request owner; geometry resources remain child service owner.
- Contracts/invariants: cache ownership, graph freshness, close semantics, public identity and delegation are preserved.
- Tests: dedicated hostile tests plus historical V1.42–V1.45 and V1.66–V1.70 integration coverage.
- Cache/fingerprint/provenance: no policy or algorithm changes; only session ownership location changes.
- Persistence/database: no consumer or schema impact.
- Determinism: five production cases must retain exact SVG/camera/visibility/cache identities.
- Visual: production path is touched; real five-case QA is mandatory.
- Unchanged behavior: public identity, cache lifetime, graph refresh, SVG, camera geometry and visibility/occlusion.

## Reopen conditions

If graph analysis reveals a new SCC, a second owner, a new cache/persistence/fingerprint consumer, a changed renderer result, or a stale truth line range, reopen IMPACT before continuing.
