# Evidence — CMP-EYE-HIGHLIGHT V1.88

- `EVD-HIGHLIGHT-001`: baseline package identity — exact V1.87 ZIP SHA-256
  `fe85b5465824336153ca2baf5eedbe6eae215edaaa25f14243a97d2c7995fba6`.
- `EVD-HIGHLIGHT-002`: owner implementation — `highlights/spec.py:8-35`, V1.88.
- `EVD-HIGHLIGHT-003`: focused tests — `test_v188_highlight_input_hardening.py:8-66`, 60 PASS.
- `EVD-HIGHLIGHT-004`: direct render consumer — `eye_svg_effects.py:209-231`, unchanged.
- `EVD-HIGHLIGHT-005`: visibility relation — `visibility.py:24,43-52`, unchanged.
- `EVD-HIGHLIGHT-006`: cache exclusion — `generator.py:192-226` plus `V1.88_CACHE_IDENTITY.json`, PASS.
- `EVD-HIGHLIGHT-007`: dependency/source identity — V1.88 artifacts report 209 modules, 567 edges, 0 new SCC, 0 duplicates,
  exactly one changed runtime source file.
- `EVD-HIGHLIGHT-008`: database identity — 8 migrations, 0 added/removed/changed.
- `EVD-HIGHLIGHT-009`: visual differential — six valid cases, SVG hashes identical, PNGs generated and inspected.
- `EVD-HIGHLIGHT-010`: benchmark — constructor sanity median +117.3714%; measurement only, no optimization claim.

Every line range above is tied to the V1.88 source snapshot; no V1.87 line range is presented as current proof.
