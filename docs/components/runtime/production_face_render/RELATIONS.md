# Relations

`REL-PFR-001`: `ProductionRenderSession.render_face` → this owner — real parent/consumer boundary.
`REL-PFR-002`: this owner → generic resolution owner.
`REL-PFR-003`: this owner → geometry service resource owner → geometry generator/cache.
`REL-PFR-004`: this owner → spatial transform owner.
`REL-PFR-005`: this owner → production visual-style owner → renderer-facing visual contracts.
`REL-PFR-006`: this owner → SVG renderer.
`REL-PFR-007`: this owner → face-overlap/Hair/Ear/Head/Ear relation owners.
`REL-PFR-008`: this owner → `CMP-RUNTIME-PRODUCTION-RENDER-RESULT` — immutable output contract.

The result class itself is no longer a responsibility of this component. No relation changes generic ownership of
geometry, appearance, visibility, cache or persistence.
