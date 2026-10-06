# Invariants and assumptions

`INV-PVS-001`: root style is supplied from the same `ResolvedComponent` already returned to `ProductionRenderResult`.
`INV-PVS-002`: no root resolution is repeated by the adapter.
`INV-PVS-003`: owner extraction from primitives/surfaces remains semantically identical to the former caller.
`INV-PVS-004`: owner iteration is sorted and therefore deterministic.
`INV-PVS-005`: unknown non-root owners remain ignored; known owners resolve through the canonical resolver.
`INV-PVS-006`: context/version/cache are forwarded unchanged and no alternate fingerprint is constructed.
`INV-PVS-007`: style resolution never mutates geometry, topology, cache lifetime or persistence.

Assumption: `RuntimeGraph` and `resolve_component` continue to enforce topology freshness and complete resolution fingerprints.
