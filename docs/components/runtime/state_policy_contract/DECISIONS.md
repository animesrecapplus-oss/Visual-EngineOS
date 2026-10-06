# Decisions

`DEC-SPC-001`: V1.72 fresh audit selects the existing immutable state-policy value contracts as one independent responsibility.
`DEC-SPC-002`: move only `StateActivation` and `StateDecision`; keep all resolver functions in `state_policy`.
`DEC-SPC-003`: retain existing production/public imports through `state_policy` so the extraction changes ownership without broadening the source delta.
`DEC-SPC-004`: no new validation semantics are added because the extraction must preserve the existing contract exactly.
`DEC-SPC-005`: freeze COLOR, persistence/database, cache policy, fingerprint algorithms, geometry and renderer semantics.
