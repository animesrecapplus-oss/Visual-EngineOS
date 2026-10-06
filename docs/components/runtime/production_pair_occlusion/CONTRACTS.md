# Contracts

`CON-PAIR-001`: target and occluder IDs are distinct and non-empty.
`CON-PAIR-002`: depths, opacity and transmission are finite; opacity/transmission are in `[0,1]`.
`CON-PAIR-003`: both owners expose exactly one semantic area region in this bounded adapter.
`CON-PAIR-004`: `coplanar_occludes` and `include_attribution` are strict booleans.
`CON-PAIR-005`: generic visibility remains authoritative; attribution is computed only when requested.
`CON-PAIR-006`: returned target/occluder IDs and RegionMaps preserve ownership.
