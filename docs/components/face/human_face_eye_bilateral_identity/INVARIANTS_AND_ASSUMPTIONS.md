# Invariants and assumptions — CMP-FACE-EYE-BILATERAL

- `INV-FEB-001`: `left_eye` must use `image_left` in the existing HumanFace production identity.
- `INV-FEB-002`: `right_eye` must use `image_right` in the existing HumanFace production identity.
- `INV-FEB-003`: standalone/other Eye identities remain `single` rather than being reinterpreted from coordinates.
- `INV-FEB-004`: Gaze semantics remain independent of bilateral side resolution.
- `INV-FEB-005`: camera, head/face orientation and eye side remain separate channels.
- `INV-FEB-006`: side participates in the existing Eye geometry cache-input projection.

Assumptions explicitly bounded by evidence:
- `build_human_face()` is the verified source of the current `left_eye` / `right_eye` IDs.
- The existing ocular builder already defines `image_left` / `image_right` semantics.
- No generic side field on `Component` is claimed by this brick.
