# Decisions

`DEC-FPOR-001`: extract only the existing generator→occluder orchestration seam.
`DEC-FPOR-002`: keep `production_face_overlap_visibility` as the semantic owner.
`DEC-FPOR-003`: keep owner geometry injected; do not import `production_slice`.
`DEC-FPOR-004`: return `None` for unsupported generators so future variants cannot silently inherit proof.
`DEC-FPOR-005`: validate the injected owner boundary before delegating to the existing resolver.
`DEC-FPOR-006`: preserve the historical four generator mappings byte-for-byte at the result/render level.
