# Evidence

`EVD-SPC-001`: V1.72 fresh responsibility/consumer/ownership audit.
`EVD-SPC-002`: focused canonical/compatibility/immutability test report — 4 passed / 0 failed.
`EVD-SPC-003`: deterministic regression evidence: V1.71 certified 1128-test matrix reused for byte-identical unaffected source/tests; V1.72 changed-surface matrix adds 101 fresh passed tests.
`EVD-SPC-004`: compileall report — PASS.
`EVD-SPC-005`: dependency graph/cycle/duplicate audit.
`EVD-SPC-006`: production benchmark comparison against V1.71: +0.3065490398%; measurement only.
`EVD-SPC-007`: five-case real production visual QA and behavior identity.
`EVD-SPC-008`: truth validation — PASS; exact line-range validation — PASS.
`EVD-SPC-009`: artifact policy and ZIP integrity evidence.

Final implementation/tool line ranges are frozen in `MANIFEST.json` and validated by `tools/audit_v172_line_ranges.py`.
