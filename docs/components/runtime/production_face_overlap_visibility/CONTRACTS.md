# Contracts

`CON-FOV-001`: root is a `Component`; camera geometry is a `GeometryContract`.
`CON-FOV-002`: `owner_geometry` is callable and returns `(GeometryContract, finite depth)` through the existing owner contract.
`CON-FOV-003`: occluder IDs are non-empty strings and unique.
`CON-FOV-004`: Head is the target; each named child must exist and resolve to exactly one semantic area region.
`CON-FOV-005`: generic visibility and causal attribution remain the authoritative algorithms.
`CON-FOV-006`: the returned result preserves target/occluder IDs, depth values, RegionMaps, visibility and attribution.
`CON-FOV-007`: extraction is behavior-preserving; no renderer bytes, cache identity or persistence payload may change.
