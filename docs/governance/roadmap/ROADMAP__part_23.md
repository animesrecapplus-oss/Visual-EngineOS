# Roadmap — V1.64 and next frontier

## V1.64 — Production Head/Ear relation orchestration extraction

Fresh V1.63 audit did not justify another Head/Ear semantic change, visibility-depth change, COLOR change or renderer change. It exposed one
existing production orchestration seam: the session still directly looped over the two Ear children and called the canonical Head/Ear leaf.

Implemented one owner only:
- `CMP-RUNTIME-PRODUCTION-HEAD-EAR-RELATIONS` → `runtime/production_head_ear_relations.py:18-65`.
- Head geometry/depth is extracted once through the canonical owner-geometry callable.
- The existing resolved Head visual is injected; appearance is not resolved a second time.
- The existing `production_head_ear_occlusion` leaf remains the semantic owner.

## V1.65 — Production face-overlap relation orchestration extraction

Fresh V1.64 audit found one existing production orchestration seam in `ProductionRenderSession.render_face`: the generator-specific
Head→Nose/Mouth child selection and call into the already-canonical face-overlap visibility owner.

Implemented one owner only:
- `CMP-RUNTIME-PRODUCTION-FACE-OVERLAP-RELATIONS` → `runtime/production_face_overlap_relations.py:26-61`.
- The four already-proven generator mappings are explicit; unknown generators do not acquire proof.
- The canonical owner geometry extractor is injected.
- `production_face_overlap_visibility` remains the semantic leaf owner.

## V1.66 — Production geometry service lifecycle extraction

Fresh V1.65 audit found one existing independent lifecycle seam: production registry/service construction and teardown around the session-owned
`GeometryCache`.

Implemented one owner only:
- `CMP-RUNTIME-PRODUCTION-GEOMETRY-SERVICE-RESOURCES` → `runtime/production_geometry_service_resources.py:11-39`.
- `ProductionRenderSession` remains the canonical cache owner.
- The new owner never clears or constructs the cache; it only owns registry/service references.

A first broader resource extraction failed two historical cache-owner tests. The scope was reopened and narrowed before certification.
Exact V1.65→V1.66 five-case identity is the release gate. No COLOR, database, persistence, cache-policy or fingerprint semantic change is
authorized.

## V1.67 rule

Start from the fresh certified V1.66 checkpoint. Do not extract the remaining render pipeline, result contract, renderer, COLOR, cache or
persistence responsibility until a new read-only audit proves a real owner, consumer, contracts, relations and impact.
