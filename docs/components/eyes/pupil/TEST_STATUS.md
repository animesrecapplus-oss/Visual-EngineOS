# Pupil test status — V1.82

Focused Pupil suite: existing local contract/adversarial/interaction tests plus
`tests/components/face/eyes/pupil/test_v182_pupil_input_hardening.py:1-30` — PASS.

The focused V1.82 gate covers bool/non-Real numeric state, non-finite outline width and valid outline width.

Integration covers EyeAppearance, styles, generator/cache-input construction, compatibility exports, ocular geometry,
SVG and vertical slices through the existing eye regression suite.

Visual acceptance: valid production render invariance only; no artistic-quality claim.

Final V1.82 regression: 153 test files / 1199 collected / 1198 PASS / 1 expected PostgreSQL SKIP / 0 FAIL.
The initial monolithic invocation timed out and was not counted; all three test trees were then completed in deterministic
batches. Compileall, dependency graph, duplicate scan, database identity, benchmarks, truth validation and visual invariance PASS.
