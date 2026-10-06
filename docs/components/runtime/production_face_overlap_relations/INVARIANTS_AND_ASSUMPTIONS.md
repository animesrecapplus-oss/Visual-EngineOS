# Invariants and assumptions

`INV-FPOR-001`: the four generator→occluder mappings remain exactly those already proven in V1.64.
`INV-FPOR-002`: unknown generators do not acquire an inferred overlap proof.
`INV-FPOR-003`: supported generators delegate to the canonical face-overlap visibility owner.
`INV-FPOR-004`: owner geometry is validated at this boundary before semantic region mapping.
`INV-FPOR-005`: no SVG mutation is performed by relation proof resolution.
`INV-FPOR-006`: generator order and occluder tuple order are deterministic.
`INV-FPOR-007`: extraction preserves the V1.64 production SVG/result identity.

Assumption: the four generator strings are existing certified production variants, not a generic
future-generator wildcard.
