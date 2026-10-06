# Adversarial test matrix — CMP-FACE-EYE-BILATERAL

| ID | Case | Expected |
|---|---|---|
| `ADV-FEB-001` | standalone `Eye` with id `left_eye` | remain `single`; no parent means no HumanFace promotion |
| `ADV-FEB-002` | parented `Eye` with unrelated id | remain `single`; no coordinate inference |
| `ADV-FEB-003` | HumanFace left/right normal render | left medial side faces pair centre; right mirrors |
| `ADV-FEB-004` | HumanFace ±30° rotation / zoom interaction | bilateral identity remains unchanged by parent/camera transform |

Negative-space checks:
- changing Gaze must not decide side;
- changing camera must not decide side;
- changing Eye x-coordinate alone must not promote a standalone Eye into a bilateral side;
- the right-eye production geometry must not change merely because the left-eye correction is applied.
