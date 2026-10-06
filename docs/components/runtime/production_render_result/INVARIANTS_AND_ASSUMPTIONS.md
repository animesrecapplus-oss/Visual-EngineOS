# Invariants and assumptions

`INV-PRR-001`: result instances are immutable and slot-based.
`INV-PRR-002`: the result carries existing values; it does not compute them.
`INV-PRR-003`: field order remains stable for positional construction in the canonical producer.
`INV-PRR-004`: compatibility/public imports are identity-compatible with the canonical owner.
`INV-PRR-005`: result ownership does not become a cache, fingerprint, persistence or renderer owner.

Assumption: the existing producer continues to construct the nine-field positional result envelope.
