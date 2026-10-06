# Adversarial test matrix

`ADV-POG-001` wrong geometry type → `TypeError`.
`ADV-POG-002` empty owner id → `ValueError`.
`ADV-POG-003` unknown owner/no surfaces → `ValueError`.
`ADV-POG-004` missing depth layer → `ValueError`.
`ADV-POG-005` conflicting depth layers → `ValueError`.
`ADV-POG-006` negative/out-of-range path index → `ValueError`.
`ADV-POG-007` deterministic path rebasing → exact expected local indices.
`ADV-POG-008` production integration → all real owner extraction calls use the canonical owner.
`ADV-POG-009` cache/visual identity → SVG and resolution-cache statistics equal V1.61.
