# Decisions — CMP-FACE-EYE-BILATERAL

- `DEC-FEB-001`: fix the verified HumanFace→Eye production boundary, not Gaze.
- `DEC-FEB-002`: preserve standalone Eye behavior; do not derive side from x/y coordinates because that would silently reinterpret independently authored Eyes.
- `DEC-FEB-003`: use the existing stable HumanFace child IDs `left_eye` and `right_eye` as the bounded production identity source; do not introduce a new generic `Component.side` field or persistence migration.
- `DEC-FEB-004`: remove the unused `_eye_component_inputs` duplicate rather than maintain a second side-resolution implementation.

Rejected alternatives:
- coordinate-derived side — broader implicit semantics and no verified generic contract;
- new generic Component side field — larger architecture/persistence surface than the defect requires;
- Gaze modification — wrong ownership boundary;
- renderer correction — wrong layer; geometry semantics are already wrong before rendering.
