# Contracts — CMP-FACE-EYE-BILATERAL

- `CON-FEB-001`: `EyeGeometryInputs.side` remains one of the existing semantic values `single`, `image_left`, `image_right`.
- `CON-FEB-002`: the canonical `build_human_face()` children `left_eye` and `right_eye` are direct `Eye` children with authored stable IDs.
- `CON-FEB-003`: a parented `Eye` with id `left_eye` resolves to `image_left`.
- `CON-FEB-004`: a parented `Eye` with id `right_eye` resolves to `image_right`.
- `CON-FEB-005`: standalone Eyes and other Eye IDs retain `single`; no coordinate inference is introduced.
- `CON-FEB-006`: changed Eye geometry uses generator version `10` and existing `_eye_cache_inputs` already includes `side`.

Precondition: the component reaches the existing Eye generator boundary.
Postcondition: HumanFace production geometry preserves medial/lateral bilateral semantics.
Errors: no new exception class; malformed topology remains governed by existing RuntimeGraph/generator contracts.
Determinism: same component identity produces the same side value.
Persistence: no schema or migration change.
