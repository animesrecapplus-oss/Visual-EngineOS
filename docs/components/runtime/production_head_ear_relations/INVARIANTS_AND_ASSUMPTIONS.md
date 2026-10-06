# Invariants and assumptions

`INV-PHER-001`: Head geometry/depth is extracted once; both Ear relations use the same Head values.

`INV-PHER-002`: Ear order is deterministic: `left_ear`, then `right_ear`.

`INV-PHER-003`: Head effective visibility and transmission are forwarded unchanged to both leaf calls.

`INV-PHER-004`: no new resolution fingerprint or cache entry is constructed by the adapter.

`INV-PHER-005`: missing required Ear children fail closed instead of silently producing partial evidence.

Assumption: the certified production face continues to expose both named Ear children for the Hair-inclusive generator.
