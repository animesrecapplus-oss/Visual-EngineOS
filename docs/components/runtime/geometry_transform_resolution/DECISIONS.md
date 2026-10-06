# Decisions

`DEC-GTR-001`: V1.73 fresh audit selects the transform-resolution responsibility inside `geometry_transform.py`.
`DEC-GTR-002`: extract one responsibility only: `GeometryTransformResolution` plus its transform-resolution helpers.
`DEC-GTR-003`: keep `resolve_geometry_contract` in `geometry_transform.py` as the geometry-contract transformation owner/facade.
`DEC-GTR-004`: preserve all historical public import identities through compatibility imports.
`DEC-GTR-005`: freeze COLOR, cache policy, fingerprint algorithms, renderer semantics and persistence/database.
