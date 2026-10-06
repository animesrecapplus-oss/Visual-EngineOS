# Errors and corrections — CMP-RUNTIME-PLACEMENT-CONSTRAINT-CONTRACT

- `ERR-PCON-001`: first benchmark harness used a non-existent `PlacementScaleMode.NONE`; corrected to the existing `UNIFORM` enum value. This was a tooling error, not a product-code defect.
- `ERR-PCON-002`: first benchmark used generated face objects where `GeometryContract` was required; corrected to explicit renderer-neutral geometry fixtures.
- `ERR-PCON-003`: first benchmark omitted `statistics` inside the fresh-process code; corrected before recording final measurements.
- `ERR-PCON-004`: first hostile solution-order test used `Mock.name` incorrectly; corrected to real `ConstraintCheck` values.

No unresolved implementation error remains.
