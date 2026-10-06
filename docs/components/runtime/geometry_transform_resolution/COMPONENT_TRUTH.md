# Component truth

`CMP-RUNTIME-GEOMETRY-TRANSFORM-RESOLUTION`.

## Identity

`FILE-GTR-001`: `src/visual_engine/runtime/geometry_transform_resolution.py`.
`TST-GTR-001`: `tests/components/runtime/geometry_transform_resolution/test_v173_geometry_transform_resolution_truth.py`.

## Responsibility

Own the immutable `GeometryTransformResolution` value and deterministic local→world→scene→camera transform resolution.

## Non-responsibility

Geometry-contract transformation, renderer output, placement constraints, visibility/occlusion, appearance, COLOR,
cache policy, fingerprints, persistence/database or production request/session lifetime.
