# Adversarial test matrix

`ADV-GTR-001`: NaN z → rejected by value contract.
`ADV-GTR-002`: infinite z → rejected by value contract.
`ADV-GTR-003`: non-finite matrix → rejected by value contract.
`ADV-GTR-004`: singular local-to-world matrix → rejected by value contract.
`ADV-GTR-005`: frozen-result mutation → `AttributeError`/`TypeError`.
`ADV-GTR-006`: parent-chain order → exact matrix equality against authoritative resolver.
`ADV-GTR-007`: public/facade identity drift → dedicated owner test fails.
`ADV-GTR-008`: new import cycle → dependency gate fails closed.
`ADV-GTR-009`: render interaction regression → real normal/boundary/interaction hashes compared to V1.72.
