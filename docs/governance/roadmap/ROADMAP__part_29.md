# Roadmap — V1.73 and next frontier

## V1.73 — Geometry transform-resolution ownership extraction

Fresh V1.72 audit selected the transform-resolution responsibility embedded in `runtime.geometry_transform`.
The immutable `GeometryTransformResolution` value, parent-chain composition, placement matrix, camera matrix and
local-to-world resolution now have one canonical owner.

`runtime.geometry_transform` remains the GeometryContract frame-transformation owner and compatibility facade.
Production geometry, renderer, visibility, COLOR, cache, fingerprint and persistence semantics remain frozen.

## V1.74 rule

Start from the fresh certified V1.73 checkpoint. Re-run the read-only responsibility/consumer/contract/impact audit.
Do not assume another geometry, resolver, appearance, cache, COLOR, persistence or renderer seam without proof.
The next micro-component must have a real owner and real consumer evidence before implementation.
