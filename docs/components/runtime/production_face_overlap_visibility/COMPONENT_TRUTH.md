# Component truth

Identity: `CMP-RUNTIME-PRODUCTION-FACE-OVERLAP-VISIBILITY`.

Parent: runtime production visibility.
Children: none.
Siblings: production pair occlusion, Head/Ear adapter, Hair/Ear adapter.
Owner: `src/visual_engine/runtime/production_face_overlap_visibility.py:17-111`.

Responsibility: own the existing production Head→Nose/Mouth overlap result contract and resolve it through the authoritative generic visibility and attribution kernels.

Non-responsibility: owner-geometry extraction, anatomy generation, renderer paint order, geometry algorithms, COLOR, persistence schema, cache lifetime, or domain morphology.

The canonical owner-geometry extractor now lives in `production_owner_geometry.py` and is injected by the production session; this keeps geometry extraction separate from overlap resolution.
