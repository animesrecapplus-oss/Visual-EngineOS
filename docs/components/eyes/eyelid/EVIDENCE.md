# CMP-EYE-EYELID — evidence

- `EVD-EYELID-001`: owner `src/visual_engine/components/face/eyes/eyelid/spec.py:8-73`; verified by V1.86 line-range tool.
- `EVD-EYELID-002`: focused hostile suite `tests/components/face/eyes/eyelid/test_v186_eyelid_input_hardening.py:1-100`;
  93/93 PASS.
- `EVD-EYELID-003`: pre-change reproduction on V1.85 accepted bool enable values and non-finite width/offset/width
  fields; recorded in `PRECHANGE_IMPACT_AUDIT_V1.86.md`.
- `EVD-EYELID-004`: source identity must show exactly one runtime file changed from V1.85.
- `EVD-EYELID-005`: dependency/cycle audit must preserve baseline graph and SCC set.
- `EVD-EYELID-006`: full regression must pass with only the documented PostgreSQL environment skip, if present.
- `EVD-EYELID-007`: production visual differential must produce and inspect actual SVG/PNG artifacts for normal,
  boundary and interaction cases.
- `EVD-EYELID-008`: hostile review exposed large-integer overflow behavior; the revised guard and focused regression are the evidence for its closure.
- `EVD-EYELID-009`: ZIP integrity and artifact cleanup must be verified before certification.

Line ranges are tied to V1.86 and must not be reused as evidence for another version.
