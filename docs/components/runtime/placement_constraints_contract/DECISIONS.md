# Decisions — CMP-RUNTIME-PLACEMENT-CONSTRAINT-CONTRACT

- `DEC-PCON-001`: select the contract portion of `runtime.placement_constraints` because it is independently typed, immutable and consumed by relation compilation.
- `DEC-PCON-002`: make `placement_constraints_contract.py` the sole runtime owner of extracted value types.
- `DEC-PCON-003`: keep geometry validation and constrained placement resolution in `placement_constraints.py`.
- `DEC-PCON-004`: use TYPE_CHECKING for `PlacementSolution` to preserve dependency direction.
- `DEC-PCON-005`: preserve legacy/public object identity and production behavior.
