# Adversarial test matrix

`ADV-FPOR-001`: non-Component root → rejected.
`ADV-FPOR-002`: non-GeometryContract camera geometry → rejected.
`ADV-FPOR-003`: empty/non-string generator → rejected.
`ADV-FPOR-004`: non-callable owner geometry → rejected.
`ADV-FPOR-005`: unsupported generator → no proof (`None`).
`ADV-FPOR-006`: invalid owner geometry type → rejected before region mapping.
`ADV-FPOR-007`: NaN owner depth → rejected.
`ADV-FPOR-008`: boolean depth → rejected.
`ADV-FPOR-009`: direct resolver result must equal session result for all supported generators.
`ADV-FPOR-010`: hidden Head preserves geometric overlap and optical visibility semantics.

No division, arithmetic transformation or cache mutation is introduced by this adapter.
