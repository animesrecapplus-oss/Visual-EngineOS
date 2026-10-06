# Contracts

`CON-FPOR-001`: root is a `Component`.
`CON-FPOR-002`: camera geometry is a `GeometryContract`.
`CON-FPOR-003`: generator is a non-empty string.
`CON-FPOR-004`: owner geometry is callable and returns a `GeometryContract` plus finite numeric depth.
`CON-FPOR-005`: only the four certified generator variants acquire a face-overlap proof.
`CON-FPOR-006`: generator `face.human_with_eyes_nose` uses `("nose",)`; the three richer face variants use
`("nose", "mouth")`.
`CON-FPOR-007`: visibility and attribution remain owned by `production_face_overlap_visibility` and the generic kernels.
`CON-FPOR-008`: supported production output is behavior-identical to V1.64.
