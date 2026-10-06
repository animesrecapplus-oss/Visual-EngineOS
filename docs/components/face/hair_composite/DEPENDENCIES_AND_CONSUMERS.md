# Dependencies and consumers — CMP-FACE-HAIR-COMPOSITE

Real dependencies: V1.56 `ear_composite`, `merge_geometry_contracts`, `Hair` geometry,
`stable_digest` and the registered generator contract.

Real consumers:
- `production_registry.py:21-22` registers the composite.
- `production_slice.py:98-142` requests it by default.
- generic camera transform and SVG renderer consume its output.

The composite does not call the database or COLOR resolver directly.
