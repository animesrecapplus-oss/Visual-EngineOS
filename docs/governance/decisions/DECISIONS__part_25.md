# Decisions — V1.91

- `DEC-FEB-001`: classify the defect at the HumanFace→Eye input boundary, not Gaze.
- `DEC-FEB-002`: use the existing stable `left_eye` / `right_eye` HumanFace child identities; do not infer side from coordinates.
- `DEC-FEB-003`: preserve standalone/other Eye behavior as `single` and avoid a new generic `Component.side` field.
- `DEC-FEB-004`: remove the unused `_eye_component_inputs` duplicate so there is one side-resolution owner.
- `DEC-FEB-005`: bump `EYE_GEOMETRY_GENERATOR_VERSION` from `9` to `10` because default generated geometry semantics changed.
- `DEC-FEB-006`: do not modify the existing cache algorithm; `_eye_cache_inputs` already includes `side` and therefore already captures the corrected geometry identity.
- `DEC-FEB-007`: do not optimize the measured +6.10% input-boundary diagnostic delta without evidence of production impact; the corrective mapping is already minimal.
- `DEC-FEB-008`: no complete-current-suite PASS is declared because the monolithic run exceeded the execution wall-clock limit; certification claims are bounded to executed evidence.
