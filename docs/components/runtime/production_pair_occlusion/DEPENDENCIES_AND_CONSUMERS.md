# Dependencies and consumers

Dependencies: `generic_geometry_region_map`, `Occluder`, `resolve_visibility`, optional `resolve_visibility_attribution`.

Real consumers:
- `production_hair_ear_occlusion.py:73-76` requests visibility + attribution.
- `production_head_ear_occlusion.py:73-76` requests visibility only because no Head/Ear attribution consumer exists.

Public export: `runtime/__init__.py:247-255`.
Database: no direct connector, SQL or migration.
COLOR: no semantic consumer.
