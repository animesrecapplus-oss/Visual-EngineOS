# Dependencies and consumers — CMP-VBOOL-001

## Real consumers

- `CON-VBOOL-001`: `runtime.visibility` imports the canonical boolean contracts/functions for historical compatibility.
- `CON-VBOOL-002`: `runtime.__init__` exposes the canonical boolean API directly.
- `TST-VBOOL-001`: historical visibility-kernel tests consume the public API.
- Production visibility uses the unchanged `runtime.visibility.resolve_visibility` path; it was re-executed for integration/visual identity but does not depend on the new owner at runtime.

## Dependencies

- `components.common.geometry_contract.GeometryContract`
- `runtime.region_geometry.geometry_to_region`
- `runtime.region_geometry.region_to_contract`
- `runtime.region_geometry._clean_polygon`
- Shapely planar boolean operations

No dependency on cache, fingerprint, provenance, COLOR, database or renderer lifecycle was introduced.
