# Dependencies and consumers — CMP-FACE-HAIR

Dependencies:
- `GeometryContract` and `GeometrySurface`.
- `Component`.
- `RegisteredGeometryGenerator`.

Real consumers:
- `production_registry.py:21-23` registers the leaf.
- `hair_composite.py:31-74` consumes the child geometry.
- `production_slice.py:98-158` reaches Hair through the production registry and interaction adapter.
- `geometry_svg.py:48-63,197-211` consumes Hair depth and role metadata.
- `production_hair_ear_occlusion.py:66-91` consumes Hair geometry/depth as the real occluder.

The Hair leaf does not own the occlusion algorithm, even though the production relation now exists.
No direct COLOR or database migration consumer is introduced.
