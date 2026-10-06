# Contracts

`CON-PVS-001`: graph is a validated `RuntimeGraph`; component ID is a non-empty string; camera geometry is a `GeometryContract`.
`CON-PVS-002`: root visual is the already-resolved `ResolvedVisualContract` for the requested component.
`CON-PVS-003`: owner IDs are collected from primitive `component_id` and surface `source_component_id` metadata.
`CON-PVS-004`: owner IDs are sorted deterministically; root is inserted first; unknown non-root owners are ignored as before.
`CON-PVS-005`: child-owner appearance is resolved only through `resolve_component`, preserving its context/version/cache inputs.
`CON-PVS-006`: returned mapping is renderer-facing only; it does not mutate geometry or visual contracts.
`CON-PVS-007`: the extracted path preserves the pre-V1.61 production SVG and cache behavior exactly.
