# Impact map

Affected:
- `production_pair_occlusion.py:17-107` — new canonical owner.
- `production_hair_ear_occlusion.py:16-77` — delegates to canonical owner.
- `production_head_ear_occlusion.py:16-78` — new domain adapter.
- `production_hair_ear_occlusion.py:67-76` and `production_head_ear_occlusion.py:70-78` — domain adapters request the canonical pair owner.
- `runtime/visibility.py:254-259` — required coplanar depth-contract correction.
- `runtime/__init__.py:247-255` — public API.

Unchanged: database schema, COLOR, cache ownership, geometry generators.
