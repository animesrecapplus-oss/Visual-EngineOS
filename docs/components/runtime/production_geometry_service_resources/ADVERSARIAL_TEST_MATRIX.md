# Adversarial test matrix

`ADV-GSR-001` wrong cache type → `TypeError` at the new boundary → PASS.

`ADV-GSR-002` access after close → `RuntimeError` → PASS.

`ADV-GSR-003` repeated close → no exception → PASS.

`ADV-GSR-004` session-created cache must still clear at session close → PASS.

`ADV-GSR-005` injected cache must survive session close → PASS through existing V1.145/V1.146 tests.

`ADV-GSR-006` same production request after extraction → exact geometry/cache/SVG identity → PASS.

`ADV-GSR-007` dependency graph cycle → 3 pre-existing SCCs, 0 new → PASS.

`ADV-GSR-008` exact duplicate implementation → 0 duplicate groups → PASS.

`ADV-GSR-009` persistence/database coupling → none → PASS.

`ADV-GSR-010` COLOR semantic mutation → none → PASS.

`ADV-GSR-011` NaN/∞/zero/negative geometry values are outside this owner; no numeric operation is introduced → NOT_APPLICABLE.
