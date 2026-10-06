# Impact map

Affected:

- `hair.py:46-48` — depth contract.
- `production_hair_ear_occlusion.py:66-91` — consumer.
- `production_slice.py:151-158` — production integration.
- `geometry_svg.py:48-63` — existing renderer consumer.
- tests and visual evidence.

Unchanged: database schema, COLOR implementation, generic visibility kernel, Ear geometry.

Cache/fingerprint: no new cache key; existing generated geometry remains content-addressed through the established generation path.
