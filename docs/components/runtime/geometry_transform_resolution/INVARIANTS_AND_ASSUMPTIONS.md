# Invariants and assumptions

`INV-GTR-001`: `GeometryTransformResolution` is frozen and slotted.
`INV-GTR-002`: all stored matrices are finite.
`INV-GTR-003`: local-to-world is invertible above the existing `1e-15` determinant threshold.
`INV-GTR-004`: z accumulation is deterministic and preserves existing world/scene/camera formulas.
`INV-GTR-005`: no geometry contract is mutated during transform resolution.
`INV-GTR-006`: compatibility exports resolve to the canonical owner.

Assumption: `geometry_contract_transform` remains the sole owner of transforming `GeometryContract` values.
