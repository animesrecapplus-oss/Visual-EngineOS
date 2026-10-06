# Roadmap

## V1.66 completed

Fresh V1.65 audit found an existing independent registry/service lifecycle responsibility still embedded in
`ProductionRenderSession.__init__` and `close`.

Implemented one bounded owner:
`src/visual_engine/runtime/production_geometry_service_resources.py:11-39`.

The owner constructs the existing production geometry registry and `CachedGeometryGenerator` around the
already session-owned `GeometryCache`. It releases only those service/registry references.

A first broader extraction was rejected by real historical cache-owner tests; the final scope preserves the
V1.45/V1.46 cache-owner contract exactly.

## V1.67 rule

Start from the fresh certified V1.66 checkpoint. Perform a read-only audit first. Do not extract the remaining
render pipeline, result contract, COLOR, cache, persistence or renderer responsibilities without independent
consumer/contract/impact proof.
