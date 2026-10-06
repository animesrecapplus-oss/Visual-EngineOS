# Contracts

`CON-RCMP-001`: `ResolvedComponent` is frozen and slot-based.

`CON-RCMP-002`: the result envelope carries component identity, kind, resolved visual contract, geometry,
trace, provenance, version and optional resolution fingerprint without recomputing any of them.

`CON-RCMP-003`: `ResolutionTrace` is frozen and stores deterministic string entries.

`CON-RCMP-004`: `runtime.contract.ResolvedComponent` and `runtime.ResolutionTrace` remain identity-compatible
re-exports of the canonical owner.

`CON-RCMP-005`: cache hits and misses return the same immutable result type; cache identity remains owned by
`runtime.resolution_cache` and `runtime.versioning`.
