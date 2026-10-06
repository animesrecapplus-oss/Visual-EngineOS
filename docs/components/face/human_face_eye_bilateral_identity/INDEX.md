# CMP-FACE-EYE-BILATERAL — V1.91 truth dossier

Status: CERTIFIED for the existing HumanFace `left_eye` / `right_eye` production identity propagation only.

- Identity: HumanFace→Eye bilateral side input boundary.
- Canonical runtime owner: `src/visual_engine/components/face/eyes/generator.py:156-171`.
- Boundary cleanup: stale unused `_eye_component_inputs` removed from `src/visual_engine/components/face/generators.py`.
- Parent: HumanFace; children: the two direct Eye components; siblings: other HumanFace children.
- Side contract: existing `left_eye` → `image_left`, `right_eye` → `image_right`; other/standalone Eye → `single`.
- Contracts: `CON-FEB-001..006`.
- Invariants: `INV-FEB-001..006`.
- Tests: `TST-FEB-001..005`.
- Adversarial tests: `ADV-FEB-001..004`.
- Relations: `REL-FEB-001..006`.
- Decisions: `DEC-FEB-001..004`.
- Errors: `ERR-FEB-001..003`.
- Impacts: `IMP-FEB-001..010`.
- Evidence: `EVD-FEB-001..010`.

No generic side-inference, coordinate-derived side inference, prompt compiler, Gaze, clipping/mask, COLOR or database contract is promoted by V1.91.
