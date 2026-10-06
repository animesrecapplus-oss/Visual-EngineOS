# Dependencies and consumers — CMP-FACE-EAR

## Real production consumers

- `entities/face.py:35-42` creates `left_ear` and `right_ear` with anchors, parameters and visual ownership.
- `components/face/ear_composite.py` requests both ear geometries as production dependencies.
- `runtime/generation.py` consumes the registered generator through the generic geometry cache path.
- `render/geometry_svg.py:106-211` consumes the `EAR` surface role and resolved style.
- Generic persistence serializes ear parameters/visual contract; no ear-specific schema consumer exists.

## Dependencies

`ear.py:7-9` depends only on `GeometryContract`, `Component` and `RegisteredGeometryGenerator`, plus the standard-library `math` module for the new finite-input guard.

## Persistence / database

No direct database consumer or migration exists. The V1.80 change is leaf validation only; the DB tree and generic persistence contract remain unchanged.
