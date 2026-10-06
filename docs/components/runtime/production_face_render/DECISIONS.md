# Decisions

`DEC-PFR-001`: V1.67 selected the existing render-request orchestration seam because it was a distinct production responsibility.
`DEC-PFR-002`: V1.67 initially kept immutable result assembly with the request owner for one bounded extraction.
`DEC-PFR-003`: V1.70 fresh audit proves the immutable result envelope is itself an independent contract with real consumers.
`DEC-PFR-004`: V1.70 moves only the result class; request orchestration remains here.
`DEC-PFR-005`: public and `production_slice` result compatibility identities remain preserved.
`DEC-PFR-006`: graph/cache/resource lifetime remains in `ProductionRenderSession`.
`DEC-PFR-007`: no renderer, geometry, appearance, occlusion, fingerprint, COLOR or persistence semantics change.
