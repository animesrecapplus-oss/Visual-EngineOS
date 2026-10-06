# Contracts — CMP-VBOOL-001

- `CON-VBOOL-001`: `BooleanOperation` is the closed union/intersection/difference operation set.
- `CON-VBOOL-002`: `BooleanResult` is frozen/slotted and carries operation, renderer-neutral region, area and emptiness.
- `CON-VBOOL-003`: public boolean functions accept `GeometryContract` inputs and return `RegionGeometry`/`BooleanResult` only.
- `CON-VBOOL-004`: results are cleaned before conversion back to `RegionGeometry`.
- `CON-VBOOL-005`: union of empty input returns an empty `RegionGeometry`.
- `CON-VBOOL-006`: unsupported operation values fail closed with `ValueError`.
- `CON-VBOOL-007`: coordinate frame of binary results is inherited from the first operand, matching the historical contract.
