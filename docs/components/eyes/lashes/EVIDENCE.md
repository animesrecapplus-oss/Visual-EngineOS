# CMP-EYE-LASH — evidence

Evidence identifiers are stable within the component dossier.

| ID | Claim | Source / exact location | Method |
|---|---|---|---|
| EVD-LASH-001 | canonical owner | `src/visual_engine/components/face/eyes/lashes/spec.py:1-85` | source inspection + SHA-256 |
| EVD-LASH-002 | focused hostile tests | `tests/components/face/eyes/lashes/test_v185_lash_input_hardening.py:1-95` | pytest, 56 collected/pass |
| EVD-LASH-003 | real consumers | appearance `9-37`; styles `6-74`; profiles `8-96`; upper renderer `177-222`; lower renderer `33-75`; exports `3-9` | reference/import trace |
| EVD-LASH-004 | pre-change defect | `artifacts/current/v1.85/V1.85_PRECHANGE_PROBE.json` | executable baseline probe |
| EVD-LASH-005 | source identity | `artifacts/current/v1.85/V1.85_SOURCE_IDENTITY.json` | SHA-256 manifest comparison |
| EVD-LASH-006 | dependency/cycle identity | `artifacts/current/v1.85/V1.85_DEPENDENCY_GRAPH.json` | AST dependency audit |
| EVD-LASH-007 | database identity | `artifacts/current/v1.85/V1.85_DATABASE_IDENTITY.json` | migration hash comparison |
| EVD-LASH-008 | visual invariance | `artifacts/current/v1.85/V1.85_VISUAL_INVARIANCE.json` plus four SVG/PNG cases | differential production render + inspection |
| EVD-LASH-009 | benchmark | `artifacts/current/v1.85/V1.85_BENCHMARK.json` | measured sanity benchmark |
| EVD-LASH-010 | line-range closure | `artifacts/current/v1.85/V1.85_LINE_RANGES.json` | executable marker/range verification |

## Source hashes

- `src/visual_engine/components/face/eyes/lashes/spec.py` — SHA-256 `7354809880d1202180ae791a97eee2b299bf84b2b5a6a8195b27272132e1fb96`.
- `tests/components/face/eyes/lashes/test_v185_lash_input_hardening.py` — SHA-256 `d918710814a88ab2b3d91d45443c026fb6a773411a8a4aa9a1a2825809e55cd3`.

Line ranges above are tied to the V1.85 candidate after implementation and are not historical V1.84 ranges.
