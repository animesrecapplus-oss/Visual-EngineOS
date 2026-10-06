# Adversarial test matrix

`ADV-FOV-001`: wrong root type → blocked with `TypeError`.
`ADV-FOV-002`: wrong geometry type → blocked with `TypeError`.
`ADV-FOV-003`: non-callable owner resolver → blocked with `TypeError`.
`ADV-FOV-004`: empty/duplicate/non-string IDs → blocked with `ValueError`.
`ADV-FOV-005`: missing child → blocked with `ValueError`.
`ADV-FOV-006`: owner resolver returns invalid depth → downstream `Occluder` validation blocks NaN.
`ADV-FOV-007`: real Head/Nose/Mouth overlap remains non-zero and visible fraction remains below one.
`ADV-FOV-008`: extracted result equals the pre-extraction result byte-for-byte at SVG level and value-for-value at visibility level.
