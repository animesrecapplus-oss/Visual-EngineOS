# Roadmap — V1.57 and next frontier

## Completed V1.57

1. Re-read the certified V1.56 checkpoint and all relevant governance/component truth.
2. Re-audited `domain_resolution`; no consumer was invented.
3. Selected the existing HumanFace Hair child as the next bounded production family.
4. Added one canonical Hair leaf owner.
5. Added one Hair-inclusive production composite with fingerprinted Hair dependency.
6. Added the minimal generic SVG Hair role and deterministic paint priority.
7. Preserved explicit V1.56 Ear generator compatibility.
8. Executed hostile tests, persistence round-trip, cache mutation and visibility interaction.
9. Generated and inspected real front/+12°/-12° and Hair visible/hidden evidence.
10. Measured V1.57 against the certified V1.56 benchmark artifact.
11. Completed deterministic regression inventory and artifact purge.

## Deferred by evidence

Hair strands/morphology, Hair/Ear occlusion, accessories, expression coupling and detailed material/light behavior remain separate micro-components.

`unresolved_domain_result()` remains unextracted because no real production consumer proves an independent owner.

## Next brick rule

V1.58 must start from a fresh read-only audit of certified V1.57. It must select one responsibility only after consumer, parent/child/sibling, cache/fingerprint, persistence and visual evidence are demonstrated.

## V1.58 completed

- Fresh V1.57 audit found the first real Hair/Ear overlap consumer.
- Hair depth was corrected from coplanar `0` to authored foreground `1`.
- A bounded production Hair/Ear visibility adapter was added.
- Resolved Hair visibility/opacity and material transmission are forwarded to the generic kernel.
- Real front/+12°/-12° and Hair visible/hidden QA was generated and inspected.

## V1.59 rule

Start from a fresh V1.58 certified checkpoint. Do not extend Hair/Ear, COLOR or domain-resolution seams without a new consumer/contract proof. Prefer the next production interaction only when geometry, depth and visibility evidence establish it.

## V1.59 — Head/Ear production visibility

Fresh V1.58 audit found a second real spatial relation: the HumanFace head surface overlaps the two Ear
regions by `15.5473896%` and `21.8440504%`. Renderer evidence shows Ear is painted before Head while both
surfaces remain at depth `0`; the semantic relation therefore requires explicit coplanar occlusion rather
than invented negative depth.

Implemented bounded responsibilities:
- canonical domain-neutral production target/occluder pair adapter;
- Hair/Ear migrated to that owner without changing its attribution contract;
- Head/Ear visibility adapter with no unproven attribution claim;
- generic visibility depth-result correction required by the new real consumer.

The first Head/Ear implementation computed unnecessary attribution and was rejected by measured performance;
`include_attribution=False` is now explicit. Same-process A/B measured an additional `8.28%` warm median
cost versus the same V1.59 path with Head/Ear disabled. The official V1.58 artifact comparison is recorded
as `+54.57%` and is treated as an environment-sensitive measurement, not a non-regression claim.

No COLOR, database schema, new cache owner, renderer clipping/masking or Hair morphology was introduced.

## V1.60 rule

Start from the fresh certified V1.59 checkpoint. Do not extend Head/Ear, Hair/Ear, COLOR or visibility depth
without a new real consumer/contract proof and a new impact audit.

## V1.60 — Production face-overlap visibility extraction

Fresh V1.59 audit did not justify another Head/Ear, Hair/Ear, COLOR or visibility-depth change. It instead exposed one existing
single-responsibility seam: the production Head→Nose/Mouth visibility resolver remained embedded in the caller-owned
`production_slice.py`.

Implemented one owner only:
- `CMP-RUNTIME-PRODUCTION-FACE-OVERLAP-VISIBILITY` → `runtime/production_face_overlap_visibility.py`.
- Existing `_owner_geometry` remains owned by `production_slice.py` and is injected.
- `ProductionVisibilityResolution` moves with its existing responsibility; runtime import compatibility is preserved.

Behavior identity is a hard gate: SVG, camera geometry, cache key and visibility/attribution values must remain identical.
No visual redesign, COLOR, database, cache-lifetime or generic visibility change is part of V1.60.

## V1.61 rule

Start from the fresh certified V1.60 checkpoint. Do not extract or extend another responsibility until a new read-only audit proves
its owner, real consumer, contracts, parent/children/siblings, cache/fingerprint, persistence and visual implications.


## V1.61 — Production visual-style map extraction

Fresh V1.60 audit did not justify another Head/Ear, Hair/Ear, COLOR or visibility-depth change. It instead exposed one existing production
responsibility in `ProductionRenderSession.render_face`: building the renderer-facing style map from camera-space geometry owner metadata.

Implemented one owner only:
- `CMP-RUNTIME-PRODUCTION-VISUAL-STYLES` → `runtime/production_visual_styles.py:18-66`.
- Root visual is injected from the existing `ResolvedComponent`; no duplicate root resolution is permitted.
- Non-root owners continue through `resolve_component`, preserving existing context/version/fingerprint/cache semantics.

Exact SVG/result identity versus certified V1.60 is a release gate. No COLOR, database, cache-lifetime, geometry, occlusion or renderer algorithm
change is authorized by this brick.

## V1.62 rule

Start from the fresh certified V1.61 checkpoint. Do not extract or extend another responsibility until a new read-only audit proves its owner,
real consumer, contracts, parent/children/siblings, cache/fingerprint, persistence and visual implications.

## V1.62 — Production owner-geometry extraction

Fresh V1.61 audit did not justify another appearance, COLOR, Head/Ear, Hair/Ear or visibility-depth change. It instead exposed one existing
shared production responsibility: the private owner-geometry selector in `production_slice.py` was consumed by the Head→Nose/Mouth,
Hair/Ear and Head/Ear production paths.

Implemented one owner only:
- `CMP-RUNTIME-PRODUCTION-OWNER-GEOMETRY` → `runtime/production_owner_geometry.py:8-67`.
- Existing surface selection, depth validation and path-index rebasing semantics are preserved exactly.
- `production_slice.py` no longer owns a duplicate geometry extractor; all real consumers use the canonical callable.

No geometry algorithm redesign, COLOR change, database migration, persistence consumer, cache-lifetime change or fingerprint change is authorized.
Exact V1.61→V1.62 SVG/result identity is a release gate.

## V1.63 rule

Start from the fresh certified V1.62 checkpoint. Do not extract or extend another responsibility until a new read-only audit proves its owner,
real consumer, contracts, parent/children/siblings, cache/fingerprint, persistence and visual implications.


## V1.63 — Production Hair/Ear relation orchestration extraction

Fresh V1.62 audit did not justify another geometry, visibility-depth, COLOR or appearance semantic change. It exposed one existing
single-responsibility seam: the production session still directly orchestrated Hair against left/right Ear after canonical geometry/style
resolution.

Implemented one owner only:
- `CMP-RUNTIME-PRODUCTION-HAIR-EAR-RELATIONS` → `runtime/production_hair_ear_relations.py`.
- The existing one-pair Hair/Ear adapter remains the semantic leaf owner.
- The canonical owner-geometry extractor is injected; no geometry logic is duplicated.
- Head/Ear and face-overlap orchestration remain separate.

Exact V1.62→V1.63 SVG/result identity is a release gate. No COLOR, database, persistence, cache-lifetime or fingerprint semantic change is authorized.

## V1.64 rule

Start from the fresh certified V1.63 checkpoint. Do not extract or extend another responsibility until a new read-only audit proves its owner,
real consumer, contracts, parent/children/siblings, cache/fingerprint, persistence and visual implications.

## V1.64 rule

See `ROADMAP__part_23.md` for the certified V1.64 completion and V1.65 rule.
