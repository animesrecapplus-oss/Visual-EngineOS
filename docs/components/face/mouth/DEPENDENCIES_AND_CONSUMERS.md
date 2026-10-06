# Dependencies and consumers — CMP-FACE-MOUTH

## Real production consumers

- `entities/face.py:29-34` constructs the real `Mouth` child with parameters, anchor and authored visual contract.
- `runtime/production_slice.py:98-142` consumes the production face composite.
- `components/face/production_registry.py:10-14` registers the child and composite generators.
- Generic `CachedGeometryGenerator` consumes declared geometry dependencies through the existing runtime path.
- Generic SVG rendering consumes the resulting ellipse; no mouth-specific renderer branch exists.
- Generic semantic-region/visibility kernels consume the labelled area through the existing production bridge.

## Dependencies

`mouth.py` depends on `math`, `GeometryContract`, `Component` and `RegisteredGeometryGenerator`.
The composite depends on existing face/eye preparation and `stable_digest`.
The production registry depends on the established face registry plus the mouth owners.

## Persistence / database

No direct database consumer or migration was found. Existing generic parameter/metadata persistence is sufficient and
was rechecked through the existing V1.55 persistence regression. V1.81 changes no database file.
