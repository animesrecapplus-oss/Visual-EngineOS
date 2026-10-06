# Adversarial matrix — CMP-FACE-HAIR

`ADV-FH-001` negative width/height → blocked by generator/Parameter contract.
`ADV-FH-002` NaN/∞ width/height/anchor → blocked by finite check.
`ADV-FH-003` custom input object → TypeError.
`ADV-FH-004` missing anchor → deterministic default.
`ADV-FH-005` parameter mutation → new geometry key and SVG.
`ADV-FH-006` visibility zero → only Hair paint disappears.
`ADV-FH-007` malformed composite cardinality → tested at composite boundary.
`ADV-FH-008` cache stale risk → mutation path exercised in same session.
`ADV-FH-009` persistence round-trip → parameters/anchor/visual contract preserved.
`ADV-FH-010` deterministic registry → exact generator names and kinds asserted.
