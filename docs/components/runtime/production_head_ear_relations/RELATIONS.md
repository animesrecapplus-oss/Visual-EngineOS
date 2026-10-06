# Relations

`REL-PHER-001`: `ProductionRenderSession.render_face` → Head/Ear orchestration; session remains lifecycle owner.

`REL-PHER-002`: orchestration → canonical Head/Ear leaf owner; pair semantics remain downstream.

`REL-PHER-003`: orchestration → canonical owner-geometry extractor; geometry semantics remain downstream.

`REL-PHER-004`: orchestration is sibling to Hair/Ear and face-overlap production relations; responsibilities are not merged.

`REL-PHER-005`: renderer consumes resulting SVG independently; this component never changes draw order.
