# Adversarial test matrix

`ADV-SPC-001`: compatibility/public identity mismatch → test fails if any duplicate class owner appears.
`ADV-SPC-002`: mutation of frozen activation → `AttributeError` expected.
`ADV-SPC-003`: precedence tuple drift → exact tuple assertion protects field order and semantics.
`ADV-SPC-004`: contract module accidentally owns resolver functions → explicit negative symbol assertions fail closed.
`ADV-SPC-005`: decision candidate identity drift → exact object identity assertion.
`ADV-SPC-006`: import-cycle audit → new module must introduce no SCC.
`ADV-SPC-007`: duplicate-function audit → no duplicate resolver implementation is allowed.
`ADV-SPC-008`: production behavior identity → five-case production evidence must remain equal to V1.71.

No `DECLARED` or `BLOCKED` case is counted as PASS.
