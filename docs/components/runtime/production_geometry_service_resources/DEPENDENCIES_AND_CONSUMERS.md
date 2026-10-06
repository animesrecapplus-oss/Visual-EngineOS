# Dependencies and consumers

## Real consumer

`src/visual_engine/runtime/production_render_session.py:10,40,108` imports, constructs, consumes and closes
the resource owner. This is the only direct production consumer.

## Dependencies

- `production_face_geometry_registry` — existing production registry factory;
- `CachedGeometryGenerator` — existing generation service;
- `GeometryGeneratorRegistry` — explicit registry type contract;
- `GeometryCache` — caller/session-owned cache supplied by the parent.

## Parent/relations

Parent: `ProductionRenderSession`.
Children: none.
Siblings: visual styles, owner geometry, face-overlap, Hair/Ear and Head/Ear relation owners.

No COLOR consumer, persistence/database consumer, new cache owner, or fingerprint algorithm is introduced.
