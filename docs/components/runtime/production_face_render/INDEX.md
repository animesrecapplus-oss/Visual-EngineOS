# Production face render — component dossier

Identity: `CMP-RUNTIME-PRODUCTION-FACE-RENDER`.

Owner: `src/visual_engine/runtime/production_face_render.py`.

Scope: one existing production face render request from resolved component through geometry generation, spatial transform,
renderer invocation, established relation adapters, and immutable result assembly.

The parent `ProductionRenderSession` retains lifetime, graph and cache ownership in `runtime/production_render_session.py:18-118`.
