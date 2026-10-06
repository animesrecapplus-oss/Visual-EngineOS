# Invariants and assumptions — CMP-RENDER-GEOMETRY-SVG-HAIR-ROLE

`INV-GHR-001`: role priority is deterministic.
`INV-GHR-002`: Hair fill uses the resolved owner style.
`INV-GHR-003`: no negative depth is introduced.
`INV-GHR-004`: renderer visibility semantics remain generic and unchanged.

Assumption: a single cap can use the existing path renderer; masks are not needed.
