# Dependencies and consumers

## Real production consumer

`src/visual_engine/runtime/production_render_session.py:9,63-92` imports and delegates the public `ProductionRenderSession.render_face` request.

## Other observed consumers

`tests/unit/test_v167_production_face_render.py` directly exercises the internal owner for boundary and equivalence tests.
`ProductionRenderResult` is now owned by `runtime/production_render_result.py` and remains compatibility-imported through
`production_slice.py` compatibility facade and then `runtime.__init__.py`.

## Dependencies

- `resolve_component`;
- `ProductionGeometryServiceResources`;
- `resolve_geometry_contract`;
- `resolve_production_visual_styles`;
- `render_geometry_svg`;
- face-overlap, Hair/Ear, Head/Ear and owner-geometry owners;
- canonical `ProductionRenderResult` value contract.

Parent: `ProductionRenderSession`.
Children: none.
Siblings: geometry-service resources, result contract, visual styles, owner geometry, face-overlap relations, Hair/Ear relations, Head/Ear relations.

No COLOR consumer, persistence/database consumer, cache owner or fingerprint algorithm is introduced.
