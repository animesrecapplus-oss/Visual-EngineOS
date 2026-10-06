# Dependencies and consumers — CMP-FACE-VIS-001

## Real consumers

- `visual_engine.entities.face.build_human_face`
- `components.face.hair.generate_hair_geometry`
- `components.face.generators.generate_nose_geometry`
- `runtime.ProductionRenderSession`
- production face registry and renderer

## Dependencies

`Component`, `Parameter`, `Anchor`, `GeometryContract`, `VisualContract`, and the existing production renderer.

No database consumer, COLOR transform consumer, cache-policy owner, or new generic runtime dependency was introduced.
