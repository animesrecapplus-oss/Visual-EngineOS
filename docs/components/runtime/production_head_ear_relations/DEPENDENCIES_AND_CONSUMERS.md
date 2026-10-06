# Dependencies and consumers

Real consumer: `src/visual_engine/runtime/production_face_render.py:92-94`.

Public API: `src/visual_engine/runtime/__init__.py:255,260`.

Dependencies:
- `production_head_ear_occlusion.resolve_head_ear_occlusion` — one-pair semantic owner;
- `production_owner_geometry.extract_production_owner_geometry` — owner geometry/depth owner supplied by the caller;
- `ResolvedVisualContract` — existing resolved Head appearance input;
- `GeometryContract` — existing camera-space geometry.

Parent: `ProductionRenderSession.render_face` owns lifecycle, graph, caches and request-level orchestration.
Children: none. Siblings: Hair/Ear and face-overlap production relation adapters remain separate.

No database, persistence, COLOR or new cache consumer exists.
