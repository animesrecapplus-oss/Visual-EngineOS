# Invariants and assumptions

`INV-PAIR-001`: no self-occlusion.
`INV-PAIR-002`: no non-finite scalar reaches `Occluder`.
`INV-PAIR-003`: no ambiguous multi-region owner is silently accepted.
`INV-PAIR-004`: optional attribution is `None` when no real downstream consumer requires causal attribution.

Assumption: domain adapters validate their component kinds before calling this owner.
