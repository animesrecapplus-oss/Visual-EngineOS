# V1.87 — evidence — CMP-EYE-EYEBROW

- `EVD-EYEBROW-001` — owner source: `src/visual_engine/components/face/eyes/eyebrow/spec.py:8-53`; verified by
  `verify_v187_eyebrow_truth.py`.
- `EVD-EYEBROW-002` — focused tests: `tests/components/face/eyes/eyebrow/test_v187_eyebrow_input_hardening.py:1-75`;
  72/72 PASS.
- `EVD-EYEBROW-003` — source identity: V1.86→V1.87 changed exactly the canonical eyebrow owner; 209 modules remain.
- `EVD-EYEBROW-004` — dependency graph: 209 modules, 567 edges, 3 pre-existing SCCs, 0 new SCCs, 0 duplicate groups.
- `EVD-EYEBROW-005` — database identity: 8 migrations unchanged.
- `EVD-EYEBROW-006` — visual differential: 5/5 valid cases byte-identical by SVG SHA-256; PNG artifacts generated and
  inspected for normal, boundary and explicit eyebrow-hidden interaction cases.
- `EVD-EYEBROW-007` — benchmark: three-sample sanity measurement; median +6.4807%; no optimization claim.
- `EVD-EYEBROW-008` — line-range verifier: PASS; no dossier document >150 lines.

Baseline checkpoint package: V1.86 certified ZIP, SHA-256
`952dea3321c70c74c5274002d6c3be2294ba2dc8e5ae676ff1bbbb86f95853ce`.

Visual evidence claim is limited to unchanged valid rendering. No artistic-quality claim is made.
