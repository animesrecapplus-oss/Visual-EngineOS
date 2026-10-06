# Contracts

`CON-GTR-001`: exactly one canonical `GeometryTransformResolution` class owner exists.
`CON-GTR-002`: public `runtime.GeometryTransformResolution` identity remains unchanged.
`CON-GTR-003`: matrices and z values are finite; local-to-world remains invertible.
`CON-GTR-004`: parent transforms are composed root-to-target in existing order.
`CON-GTR-005`: placement/camera defaults retain identity/default-camera semantics.
`CON-GTR-006`: `geometry_transform.resolve_geometry_contract` remains the compatibility/contract-transform facade.
