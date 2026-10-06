# Dependencies and consumers

Real consumer: `src/visual_engine/runtime/production_face_render.py:83-85`.
Public API: `src/visual_engine/runtime/__init__.py:248-261`.

Dependencies:
- `production_face_overlap_visibility` canonical resolver/result;
- `GeometryContract`;
- `Component`;
- injected `extract_production_owner_geometry` at the production boundary.

Parent: `ProductionRenderSession.render_face`.
Children: none.
Siblings: owner geometry, visual styles, Hair/Ear relations, Head/Ear relations.

Persistence/database: no direct consumer, migration, schema or SQL.
COLOR: no semantic consumer or change.
Cache/fingerprint: no new owner, no cache lookup added, no fingerprint algorithm change.
