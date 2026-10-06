# Decisions

`DEC-PVS-001`: extract only the existing production style-map construction; no geometry, rendering or occlusion concern moves.
`DEC-PVS-002`: inject the already-resolved root visual to prevent a second resolution/cache lookup.
`DEC-PVS-003`: retain the former owner-ID extraction semantics and sorted iteration order exactly.
`DEC-PVS-004`: delegate all non-root appearance resolution to `resolve_component`; no duplicate resolver is introduced.
`DEC-PVS-005`: expose the extracted owner through the runtime public API because it is now the unique callable boundary.
`DEC-PVS-006`: exact V1.60→V1.61 production identity is a hard gate; no visual redesign is authorized.
