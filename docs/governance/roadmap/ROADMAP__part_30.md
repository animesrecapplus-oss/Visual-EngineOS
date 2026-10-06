# Roadmap — V1.74 and next frontier

## V1.74 — Placement coverage ownership extraction

Fresh V1.73 audit selected the coverage-specific responsibility inside `runtime.placement` because its contract, solver and consumers were independently traceable.

Canonical owner: `runtime.placement_coverage`.
`runtime.placement` remains the general anchor/dimension/rotation/depth solver and compatibility surface.
`runtime.spatial_relationships` consumes the canonical coverage contract directly.

No COLOR, cache/fingerprint, persistence/database, visibility or renderer semantics were changed.

## V1.75 rule

Start from the fresh certified V1.74 checkpoint. Re-run the read-only responsibility/consumer/contract/impact audit. Do not assume the next seam is placement, geometry, resolver, appearance, cache, COLOR, persistence or renderer.

The next micro-component requires a real owner, real consumer evidence and its own truth dossier before implementation.
