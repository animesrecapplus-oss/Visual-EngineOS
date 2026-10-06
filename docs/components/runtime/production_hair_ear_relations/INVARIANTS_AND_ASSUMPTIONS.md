# Invariants and assumptions

`INV-PHER-001`: Hair is extracted once; both Ear relations use the same Hair geometry/depth.

`INV-PHER-002`: Ear order is deterministic: `left_ear`, then `right_ear`.

`INV-PHER-003`: Hair effective visibility and transmission are not recomputed or altered.

`INV-PHER-004`: no new resolution fingerprint or cache entry is constructed by the adapter.

`INV-PHER-005`: missing required production children fail closed instead of silently producing partial evidence.

Assumption: the certified production face continues to expose the three named children for the Hair-inclusive generator.
