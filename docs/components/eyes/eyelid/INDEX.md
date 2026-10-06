# CMP-EYE-EYELID — truth dossier index

Status: `CERTIFIED` for V1.86 local `EyelidAppearance` input-boundary hardening.

- Identity: `CMP-EYE-EYELID`
- Semantic parent: `ORBIT / PERIOCULAR` (verified architectural node)
- Aggregate parent: `CMP-EYE`
- Related siblings: Lash, Eyebrow, Caruncle, Epicanthic Fold
- Canonical owner: `src/visual_engine/components/face/eyes/eyelid/spec.py:8-73`
- Focused tests: `tests/components/face/eyes/eyelid/test_v186_eyelid_input_hardening.py:1-100`

Scope is deliberately local. No standalone eyelid geometry owner is created; geometry remains in the existing
ocular geometry/render pipeline.

Evidence and exact line ranges are recorded in `EVIDENCE.md` and verified by the V1.86 line-range tool.
