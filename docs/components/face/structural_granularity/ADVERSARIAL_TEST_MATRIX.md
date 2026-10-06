# Adversarial matrix — CMP-FACE-STRUCTURAL-GRANULARITY-AUDIT

`ADV-FSG-001`: candidate accidentally marked IMPLEMENTED → validator must reject.
`ADV-FSG-002`: invented consumer for ScalpBoundary/Hairline → audit must report none.
`ADV-FSG-003`: duplicate owner for HeadGeometry → reject; current owner remains `generators.py`.
`ADV-FSG-004`: empty speculative source directories created → reject; only documentation targets are created.
`ADV-FSG-005`: stale line range → line-range validator must reject.
`ADV-FSG-006`: non-deterministic matrix ordering → registry is sorted and validator checks stable output.
`ADV-FSG-007`: accidental COLOR/database/source mutation → source hash/graph review must show none.
