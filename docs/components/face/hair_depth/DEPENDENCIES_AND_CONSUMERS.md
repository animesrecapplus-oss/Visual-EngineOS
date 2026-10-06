# Dependencies and consumers

Dependencies:

- `GeometrySurface` from `geometry_contract.py`.
- `Component` parameters/identity.

Real consumers:

- `runtime.production_owner_geometry.extract_production_owner_geometry`: `production_owner_geometry.py:8-67` reads authored `depth_layer`.
- `runtime.production_hair_ear_occlusion`: `production_hair_ear_occlusion.py:66-91` receives the resolved Hair depth.
- `render.geometry_svg._surface_depths`: `geometry_svg.py:48-63` consumes authored depth for paint ordering.

The new V1.58 consumer is the Hair/Ear production occlusion adapter; no consumer is inferred from tests alone.
