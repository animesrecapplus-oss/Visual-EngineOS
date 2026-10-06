# Component truth — CMP-RUNTIME-PLACEMENT-CONSTRAINT-CONTRACT

## Identity

- `CMP-RUNTIME-PLACEMENT-CONSTRAINT-CONTRACT-001`
- Canonical owner: `runtime/placement_constraints_contract.py`

## Responsibility

Own immutable placement-constraint value contracts: status, constraint declarations, checks and constrained-placement result.

## Non-responsibility

No placement resolution, geometry materialization, optimization, visibility/occlusion, renderer, COLOR, cache/fingerprint/provenance or persistence.

## Real consumers

- `runtime.spatial_relationships` consumes the constraint types while compiling relation payloads.
- `runtime.__init__` exposes the public contract names.
- Historical placement-constraint tests consume the public/legacy surface.
