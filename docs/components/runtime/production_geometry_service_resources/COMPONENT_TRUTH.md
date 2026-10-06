# Component truth

`CMP-RUNTIME-PRODUCTION-GEOMETRY-SERVICE-RESOURCES`.

## Responsibility

Own construction and teardown of the production face geometry registry and its
`CachedGeometryGenerator` service for a caller-owned `GeometryCache`.

## Explicit non-responsibility

- `GeometryCache` construction, ownership, invalidation or fingerprint identity;
- `ResolutionCache` construction or ownership;
- component graph construction/rebuild;
- geometry generation algorithms;
- geometry cache policy or key semantics;
- appearance/COLOR resolution;
- spatial transform;
- renderer/SVG output;
- visibility/occlusion relations;
- persistence/database;
- production request lifecycle beyond the geometry service resources.

The cache remains owned by `ProductionRenderSession`; this boundary must never clear it.
