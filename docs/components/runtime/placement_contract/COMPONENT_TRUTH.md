# Component truth — CMP-RUNTIME-PLACEMENT-CONTRACT

## Identity

- `CMP-PLAC-001`
- Canonical owner: `runtime/placement_contract.py`

## Responsibility

Own `PlacementScaleMode`, `PlacementDepthRelation`, `AnchorReference`, `DimensionConstraint`, `PlacementIntent` and `PlacementSolution` value contracts, including solution affine-transform helpers.

## Non-responsibility

No geometry lookup/materialization, placement solving, constraint validation, visibility/occlusion, renderer, COLOR, cache/fingerprint/provenance or persistence.

## Parent / siblings

Parent: runtime spatial placement. Siblings: `placement_coverage`, `placement_constraints_contract`, `placement_visibility`.

## Real consumers

`runtime.spatial_relationships`, `runtime.placement_constraints`, `runtime.placement_visibility`, public `runtime.__init__`, and historical placement tests.
