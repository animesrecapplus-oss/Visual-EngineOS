# Adversarial test matrix

`ADV-PHER-001`: non-Component root → reject.
`ADV-PHER-002`: non-GeometryContract camera geometry → reject.
`ADV-PHER-003`: non-Mapping styles → reject.
`ADV-PHER-004`: non-callable owner geometry → reject.
`ADV-PHER-005`: missing Hair → reject.
`ADV-PHER-006`: missing Hair resolved style → reject.
`ADV-PHER-007`: missing Ear → reject.
`ADV-PHER-008`: custom owner-geometry call order must be deterministic.
`ADV-PHER-009`: hidden Hair must preserve geometric coverage while restoring optical visibility.
`ADV-PHER-010`: direct adapter result must equal the real production session result.

Scalar finiteness/range validation remains intentionally delegated to the canonical Hair/Ear leaf and pair kernels.
