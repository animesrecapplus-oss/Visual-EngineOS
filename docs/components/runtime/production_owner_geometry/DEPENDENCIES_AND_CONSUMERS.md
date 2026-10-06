# Dependencies and consumers

Real production consumers:
- `src/visual_engine/runtime/production_face_render.py:84,90,93` injects the extractor for face-overlap, Hair/Ear and Head/Ear; the relation owners then consume the same canonical callable.
- `src/visual_engine/runtime/production_hair_ear_relations.py:20-59` owns the extracted Hair/Ear orchestration and injects the same canonical callable.
- `src/visual_engine/runtime/production_face_overlap_visibility.py:57-61` consumes the injected callable contract.
- `src/visual_engine/runtime/production_hair_ear_occlusion.py:57-77` remains the one-pair leaf consumer through the new orchestration owner.
- `src/visual_engine/runtime/production_head_ear_occlusion.py:59-78` consumes extracted target/occluder geometry supplied by the session.

Public API: `src/visual_engine/runtime/__init__.py:247-258` exposes the canonical callable.

Dependency: `GeometryContract` only. The owner has no direct cache, fingerprint, persistence/database or COLOR dependency.
Parent: `ProductionRenderSession.render_face` owns request lifecycle and camera geometry.
Children: none. Siblings consume the result but do not own extraction.
