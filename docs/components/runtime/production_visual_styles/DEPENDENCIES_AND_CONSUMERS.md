# Dependencies and consumers

Real consumer: `src/visual_engine/runtime/production_face_render.py:78-81` builds the style map used by `render_geometry_svg`.

Public API: `src/visual_engine/runtime/__init__.py:247-258` exports the canonical adapter.

Dependencies:
- `RuntimeGraph` topology/index validation;
- `GeometryContract` owner metadata;
- `ResolvedVisualContract` root/style value;
- `resolve_component` for non-root owners;
- `ResolutionContext`, `VersionStamp`, `ResolutionCache` as delegated resolution inputs.

Parent: `ProductionRenderSession.render_face` owns lifecycle and the root `ResolvedComponent`.
Children: none.
Siblings: production overlap/occlusion adapters consume the resulting styles but do not own style resolution.

Cache/fingerprint: no new cache; child lookups use the existing resolution fingerprint/cache path unchanged.
Persistence/database: no SQL, schema, migration or persistence consumer.
COLOR: no COLOR resolver or semantic change; resolved visual contracts are consumed as already-existing renderer input.
