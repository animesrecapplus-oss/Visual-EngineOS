# Adversarial test matrix — CMP-FACE-NOSE-001

`ADV-NOSE-001`: zero/negative width or height → reject.
`ADV-NOSE-002`: non-numeric parameter → existing conversion/parameter boundary must reject.
`ADV-NOSE-003`: custom generator input → reject.
`ADV-NOSE-004`: missing/duplicate Nose child in a composite → composite must fail explicitly.
`ADV-NOSE-005`: stale dependency geometry → existing composite/cache fingerprint path must invalidate.
`ADV-NOSE-006`: Nose visual inheritance must not create a second COLOR authority.
`ADV-NOSE-007`: unsupported anatomical claims must remain documentation-only.
