# Adversarial matrix — CMP-EYE-HIGHLIGHT

- `ADV-HIGHLIGHT-001`: NaN for every numeric field — PASS, rejected.
- `ADV-HIGHLIGHT-002`: +∞ and -∞ for every numeric field — PASS, rejected.
- `ADV-HIGHLIGHT-003`: bool in every numeric field — PASS, rejected.
- `ADV-HIGHLIGHT-004`: numeric strings in every numeric field — PASS, rejected.
- `ADV-HIGHLIGHT-005`: 10**10000 in every numeric field — PASS, rejected as ValueError rather than leaking OverflowError.
- `ADV-HIGHLIGHT-006`: unknown string/None/int shape — PASS, rejected.
- `ADV-HIGHLIGHT-007`: unhashable/opaque shape values — PASS, rejected.
- `ADV-HIGHLIGHT-008`: negative width/height and opacity outside [0,1] — PASS, existing rejection retained.
- `ADV-HIGHLIGHT-009`: valid boundary zero dimensions, alpha color and ±360 rotation — PASS.
- `ADV-HIGHLIGHT-010`: visibility-hidden rendering remains valid and unchanged — PASS by differential visual QA.

Property-based testing: NOT_AVAILABLE because Hypothesis is not installed in the certified environment.
Deterministic parameterized adversarial coverage is used instead.
