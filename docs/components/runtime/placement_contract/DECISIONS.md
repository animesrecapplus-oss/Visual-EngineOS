# Decisions — CMP-RUNTIME-PLACEMENT-CONTRACT

- `DEC-PLAC-001`: select immutable placement value contracts after a fresh V1.76 consumer/ownership audit proved a separate responsibility.
- `DEC-PLAC-002`: make `placement_contract.py` the sole runtime owner of extracted placement value types.
- `DEC-PLAC-003`: retain solving/materialization in `placement.py`.
- `DEC-PLAC-004`: preserve historical imports through canonical aliases.
- `DEC-PLAC-005`: keep `CoverageIntent` as a real dependency because `PlacementIntent.coverage` is an existing contract field.
- `DEC-PLAC-006`: update `placement_constraints_contract` TYPE_CHECKING dependency to point at the canonical placement contract owner.
