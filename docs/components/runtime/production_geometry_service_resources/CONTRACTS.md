# Contracts

`CON-GSR-001`: constructor requires a real `GeometryCache` instance.

`CON-GSR-002`: construction creates the existing production face geometry registry and one
`CachedGeometryGenerator` bound to the supplied cache.

`CON-GSR-003`: `geometry_service` returns the constructed service while the resource is open.

`CON-GSR-004`: access after close fails with `RuntimeError`; no partially released service is returned.

`CON-GSR-005`: `close()` is idempotent.

`CON-GSR-006`: `close()` releases only registry/service references and never clears the supplied cache.

`CON-GSR-007`: supported production render output and cache identities remain identical to V1.65.
