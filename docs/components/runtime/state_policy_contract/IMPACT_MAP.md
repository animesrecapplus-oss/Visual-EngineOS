# Impact map

`IMP-SPC-001`: create one canonical contract module and reduce `state_policy.py` to resolver ownership plus compatibility imports.
`IMP-SPC-002`: preserve existing `consequence_bindings`, `resolution_context` and public runtime imports through the compatibility facade; no unrelated consumer rewiring is needed.
`IMP-SPC-003`: preserve `StateActivation`/`StateDecision` identity for historical `state_policy` imports.
`IMP-SPC-004`: preserve precedence tuple and all state-resolution outputs byte-for-byte at the semantic level.
`IMP-SPC-005`: no cache/fingerprint/provenance algorithm changes.
`IMP-SPC-006`: no persistence/database consumer or schema impact.
`IMP-SPC-007`: no COLOR semantic change.
`IMP-SPC-008`: production render behavior must remain identical to V1.71; visual QA is required because state resolution is upstream of rendering.
`IMP-SPC-009`: dependency graph must add no SCC and no duplicate implementation.
