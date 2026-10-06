# Adversarial test matrix

`ADV-PRS-001`: invalid root type → `TypeError`.
`ADV-PRS-002`: render/graph/refresh after close → `RuntimeError`.
`ADV-PRS-003`: repeated close → idempotent, no second teardown.
`ADV-PRS-004`: stale topology → render rejected until explicit `refresh()`.
`ADV-PRS-005`: injected cache lifetime → cache objects and entries survive session close.
`ADV-PRS-006`: compatibility/public identity → no duplicate session class.
`ADV-PRS-007`: cycle audit → no new SCC introduced by extraction.
`ADV-PRS-008`: deterministic production output → five-case SVG/camera/visibility/cache identity preserved.
`ADV-PRS-009`: extreme ownership state → no second cache owner, fingerprint owner or persistence owner introduced.

No `DECLARED` or `BLOCKED` case is counted as PASS.
