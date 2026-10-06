# Dependencies and consumers — CMP-PCOV-001

## Real consumers

- `REL-PCOV-001`: `runtime.placement` imports the canonical contract and calls the solver during `resolve_placement`.
- `REL-PCOV-002`: `runtime.spatial_relationships` imports the canonical `CoverageIntent` when compiling relation metadata.
- `REL-PCOV-003`: `runtime.__init__` exposes `CoverageIntent` directly from the canonical owner.
- Existing placement tests consume the public placement API; they remain compatibility evidence.

## Dependencies

- `shapely.affinity` and `shapely.geometry.Point` perform region transforms and anchor containment checks.
- `runtime.region_geometry` is used by the placement consumer to materialize `GeometryContract` regions; the new owner receives regions, so it does not own geometry-contract conversion.

## Ownership direction

`spatial_relationships → placement_coverage`; `placement → placement_coverage`. The new owner does not import either consumer.
