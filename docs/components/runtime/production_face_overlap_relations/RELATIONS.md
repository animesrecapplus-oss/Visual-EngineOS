# Relations

`REL-FPOR-001`: ProductionRenderSession → face-overlap relation adapter; lifecycle remains session-owned.
`REL-FPOR-002`: relation adapter → canonical production face-overlap visibility owner.
`REL-FPOR-003`: relation adapter → injected owner geometry; no reverse dependency on `production_slice`.
`REL-FPOR-004`: relation proof → `ProductionRenderResult.visibility` compatibility field.
`REL-FPOR-005`: relation proof and SVG rendering consume the same camera-space geometry but remain parallel.
`REL-FPOR-006`: Hair/Ear and Head/Ear relation adapters remain independent siblings.
