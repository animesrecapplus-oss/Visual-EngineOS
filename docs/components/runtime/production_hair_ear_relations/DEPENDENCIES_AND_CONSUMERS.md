# Dependencies and consumers

Real consumer: `src/visual_engine/runtime/production_face_render.py:88-91`.

Public API: `src/visual_engine/runtime/__init__.py:253-260`.

Dependencies:
- `production_hair_ear_occlusion.resolve_hair_ear_occlusion` — one-pair semantic owner;
- `production_owner_geometry.extract_production_owner_geometry` — owner geometry/depth owner;
- `ResolvedVisualContract` — existing resolved Hair appearance input;
- `GeometryContract` — existing camera-space geometry.

Parent: `ProductionRenderSession.render_face` owns lifecycle, graph, caches and request-level orchestration.
Children: none. Siblings: face-overlap and Head/Ear production adapters remain separate.

No database, persistence, COLOR or new cache consumer exists.
