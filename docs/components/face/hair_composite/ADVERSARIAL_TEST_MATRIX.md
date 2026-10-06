# Adversarial matrix — CMP-FACE-HAIR-COMPOSITE

`ADV-FHC-001` negative width/height → blocked by generator/Parameter contract.
`ADV-FHC-002` NaN/∞ width/height/anchor → blocked by finite check.
`ADV-FHC-003` custom input object → TypeError.
`ADV-FHC-004` missing anchor → deterministic default.
`ADV-FHC-005` parameter mutation → new geometry key and SVG.
`ADV-FHC-006` visibility zero → only Hair paint disappears.
`ADV-FHC-007` malformed composite cardinality → tested at composite boundary.
`ADV-FHC-008` cache stale risk → mutation path exercised in same session.
`ADV-FHC-009` persistence round-trip → parameters/anchor/visual contract preserved.
`ADV-FHC-010` deterministic registry → exact generator names and kinds asserted.
