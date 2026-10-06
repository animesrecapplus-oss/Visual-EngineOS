# Impact map — CMP-RUNTIME-PLACEMENT-CONSTRAINT-CONTRACT

- `IMP-PCON-001`: source split between new canonical contract owner and existing validation/resolution facade.
- `IMP-PCON-002`: `runtime.spatial_relationships` remains the real algorithm consumer of the contracts.
- `IMP-PCON-003`: `runtime.__init__` public exports now import contract values from the canonical owner.
- `IMP-PCON-004`: cache/fingerprint/provenance semantics unchanged.
- `IMP-PCON-005`: no persistence/database schema or migration consumer found.
- `IMP-PCON-006`: deterministic ordering and frozen-result semantics preserved.
- `IMP-PCON-007`: production SVG/camera hashes are unchanged for normal, boundary and interaction cases.
- `IMP-PCON-008`: existing placement validation/resolution behavior remains in the historical module.
