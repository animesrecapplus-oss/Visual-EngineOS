# Adversarial test matrix

`ADV-PFR-001` invalid root type → `TypeError`.

`ADV-PFR-002` invalid graph type → `TypeError`.

`ADV-PFR-003` invalid resources/cache type → `TypeError`.

`ADV-PFR-004` empty component ID → `ValueError`.

`ADV-PFR-005` empty generator → `ValueError`.

`ADV-PFR-006` invalid context/version → `TypeError`.

`ADV-PFR-007` stale graph → blocked by the parent session before delegation.

`ADV-PFR-008` closed session → blocked by the parent lifecycle guard.

`ADV-PFR-009` injected cache ownership → historical V1.45/V1.46 tests remain passing.

`ADV-PFR-010` relation boundary → existing supported-generator mappings remain unchanged.

`ADV-PFR-011` NaN/∞/zero/negative geometry inputs → remain governed by existing geometry/transform contracts; no new arithmetic is introduced.

`ADV-PFR-012` cycle audit → no new SCC.

`ADV-PFR-013` duplicate implementation → exact-function audit reports none.

`ADV-PFR-014` determinism → fresh V1.66 comparison and repeated production QA.
