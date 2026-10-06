# Invariants and assumptions — CMP-VBOOL-001

- `INV-VBOOL-001`: boolean contracts are immutable after construction.
- `INV-VBOOL-002`: one canonical owner exists for `BooleanOperation` and `BooleanResult`.
- `INV-VBOOL-003`: public results are renderer-neutral `RegionGeometry` values.
- `INV-VBOOL-004`: empty unions remain empty rather than fabricating geometry.
- `INV-VBOOL-005`: binary result frame follows the first operand as in V1.74.
- `INV-VBOOL-006`: no visibility depth/optical semantics are inferred by this component.

Assumption: `region_geometry` remains the authoritative GeometryContract-to-planar-region
materializer. This brick does not change that owner.
