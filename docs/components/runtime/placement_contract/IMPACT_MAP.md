# Impact map — CMP-RUNTIME-PLACEMENT-CONTRACT

- `IMP-PLAC-001`: source split between canonical value-contract owner and existing placement solver.
- `IMP-PLAC-002`: `spatial_relationships`, `placement_constraints` and `placement_visibility` retain their real consumers.
- `IMP-PLAC-003`: public runtime exports preserve object identity.
- `IMP-PLAC-004`: placement math, geometry materialization and solver ordering remain unchanged.
- `IMP-PLAC-005`: cache/fingerprint/provenance semantics unchanged.
- `IMP-PLAC-006`: no persistence/database consumer or schema change found.
- `IMP-PLAC-007`: COLOR remains untouched because no downstream COLOR consumer is involved.
- `IMP-PLAC-008`: production SVG/camera hashes remain identical for normal, boundary and interaction cases.
