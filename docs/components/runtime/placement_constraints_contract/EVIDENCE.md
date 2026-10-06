# Evidence — CMP-RUNTIME-PLACEMENT-CONSTRAINT-CONTRACT

- `EVD-PCON-001`: V1.75 certified checkpoint is the baseline.
- `EVD-PCON-002`: fresh audit found contract and validation/resolution responsibilities mixed in `placement_constraints.py`.
- `EVD-PCON-003`: new owner has 85 source lines; validation facade has 89 lines.
- `EVD-PCON-004`: canonical owner audit found exactly one owner.
- `EVD-PCON-005`: dependency audit found 0 new SCCs and 0 new exact duplicate groups.
- `EVD-PCON-006`: focused placement/relation suites pass.
- `EVD-PCON-007`: full regression passes with one expected PostgreSQL skip.
- `EVD-PCON-008`: benchmark delta is recorded as +0.780% median.
- `EVD-PCON-009`: four production visual cases have identical SVG/camera hashes to V1.75.
- `EVD-PCON-010`: truth and exact-line-range validators pass with 27 declared exact ranges (11 files + 16 dossier entries).
- `EVD-PCON-011`: final artifact cleanup leaves only `artifacts/current/v1.76/`.
- `EVD-PCON-012`: certified ZIP passes integrity verification.
