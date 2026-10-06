# Contracts — CMP-FACE-MOUTH

- `CON-MOUTH-001`: generator identity is `face.mouth@1` and supports only `Mouth`.
- `CON-MOUTH-002`: width/height must be finite positive numeric values; malformed bypassed state is rejected by the leaf owner.
- `CON-MOUTH-003`: output is one component-local ellipse primitive labelled `semantic_region=MOUTH` plus one surface at `depth_layer=1`.
- `CON-MOUTH-004`: primitive and surface carry the real mouth component owner; composition preserves that ownership.
- `CON-MOUTH-005`: `face.human_with_eyes_nose_mouth@1` requires exactly two Eyes, one Nose and one Mouth and declares all four geometry dependencies.
- `CON-MOUTH-006`: production visibility consumes the exact camera-space mouth geometry; it does not recreate a synthetic shape.
- `CON-MOUTH-007`: authored mouth appearance is a normal `VisualContract`; no COLOR-domain resolver was changed.
- `CON-MOUTH-008`: persistence uses the existing generic component payload; no mouth-specific table or migration exists.
- `CON-MOUTH-009`: bools and strings are not accepted as numeric width/height values even if `Parameter` construction was bypassed.
- `CON-MOUTH-010`: positive dimensions that collapse to a zero radius are rejected before geometry construction completes.
