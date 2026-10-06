# Relations — CMP-FACE-EYE-BILATERAL

- `REL-FEB-001`: HumanFace → direct Eye children — VERIFIED through `Component.add_child` and `build_human_face`.
- `REL-FEB-002`: `left_eye` → `image_left` — VERIFIED by existing entity identity plus current builder semantics.
- `REL-FEB-003`: `right_eye` → `image_right` — VERIFIED by existing entity identity plus current builder semantics.
- `REL-FEB-004`: Eye side → canthus/caruncle geometry — VERIFIED through `build_eye_geometry(..., side=...)`.
- `REL-FEB-005`: Eye side → geometry cache identity — VERIFIED through `_eye_cache_inputs`.
- `REL-FEB-006`: Gaze is orthogonal to side — VERIFIED by existing separate `Gaze` input and prior V1.89 certification.

No new parent-child hierarchy is introduced.
