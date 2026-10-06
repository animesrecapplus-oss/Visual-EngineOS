# Contracts — CMP-FACE-HAIR

- `CON-FH-001`: generator name `face.hair@1`, kind `Hair`.
- `CON-FH-002`: custom generator inputs are rejected; authoring parameters are read from `Component.parameters`.
- `CON-FH-003`: width and height must be finite and strictly positive.
- `CON-FH-004`: anchor coordinates must be finite; missing center uses deterministic defaults.
- `CON-FH-005`: output frame is `component`; one closed path; one `HAIR` surface; `depth_layer=0`.
- `CON-FH-006`: surface carries `component_id` so the generic resolver/renderer never guesses ownership.
- `CON-FH-007`: output remains renderer-neutral; fill/contour policy belongs to the visual contract and renderer role.

The contract does not claim hair/ear occlusion or 3D hair volume.
