# Dependencies and consumers

Real consumer:
- `src/visual_engine/runtime/production_face_overlap_relations.py:33-61` resolves the production Head→Nose/Mouth overlap result.

Public API:
- `src/visual_engine/runtime/__init__.py:247-256` exports the canonical resolver and result compatibility type.

Dependencies:
- `generic_geometry_region_map`;
- `Occluder`;
- `resolve_visibility`;
- `resolve_visibility_attribution`;
- injected `extract_production_owner_geometry` from the canonical owner.

Parent/children/siblings:
- Parent responsibility remains `ProductionRenderSession` lifecycle.
- No child component is created.
- Sibling production pair adapters remain separate owners of their domain-kind contracts.

Persistence/database: no direct SQL, schema, migration or database consumer.
COLOR: no semantic consumer or change.
Cache/fingerprint: no new cache owner and no geometry/resolution identity change.
