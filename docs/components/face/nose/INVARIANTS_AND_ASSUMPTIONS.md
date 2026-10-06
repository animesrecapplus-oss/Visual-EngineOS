# Invariants and assumptions — CMP-FACE-NOSE-001

`INV-NOSE-001`: width and height are positive before geometry construction.
`INV-NOSE-002`: command ordering is deterministic.
`INV-NOSE-003`: the main path remains the first path and the two nostril details follow it.
`INV-NOSE-004`: surface ownership is explicit and renderer-neutral.
`INV-NOSE-005`: Nose remains a child of HumanFace; no second nose owner is introduced.

Assumption: the current V1.x Nose is a stylized structural prototype, not complete nasal anatomy.
