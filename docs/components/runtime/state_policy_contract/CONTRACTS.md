# Contracts

`CON-SPC-001`: exactly one canonical `StateActivation` class owner exists.
`CON-SPC-002`: exactly one canonical `StateDecision` class owner exists.
`CON-SPC-003`: `StateActivation` retains its frozen/slotted fields and `precedence_key` semantics.
`CON-SPC-004`: `StateDecision.candidate` remains a `StateActivation` value reference without new validation semantics.
`CON-SPC-005`: `runtime.state_policy` remains an identity-compatible compatibility facade.
`CON-SPC-006`: `runtime.StateActivation` and `runtime.StateDecision` resolve to the canonical owner.
