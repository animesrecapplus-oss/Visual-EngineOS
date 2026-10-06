# Relations — CMP-RUNTIME-PLACEMENT-CONSTRAINT-CONTRACT

- `REL-PCON-001`: `runtime.placement_constraints` is the historical validation/resolution owner and compatibility facade.
- `REL-PCON-002`: `runtime.spatial_relationships` compiles external relation data into these contracts.
- `REL-PCON-003`: `runtime.__init__` is the public API facade.
- `REL-PCON-004`: `runtime.placement` resolves `PlacementSolution`; it is not a runtime dependency of the contract owner.
- `REL-PCON-005`: `region_geometry` remains responsible for geometry materialization used by validation.
- `REL-PCON-006`: no relation to COLOR/cache/fingerprint/provenance/database was changed.
