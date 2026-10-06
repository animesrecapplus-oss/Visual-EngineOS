# Component truth

`CMP-RUNTIME-PRODUCTION-FACE-OVERLAP-RELATIONS`.

Parent: runtime production render session.
Owner: `src/visual_engine/runtime/production_face_overlap_relations.py:26-61`.
Children: none.
Siblings: production face-overlap visibility, owner geometry, visual styles, Hair/Ear relations,
Head/Ear relations.

Responsibility: select the existing production Head→Nose/Mouth child set from the proven generator
variants and delegate the relation to the canonical visibility resolver.

Non-responsibility: geometry generation, owner extraction, appearance resolution, visibility math,
attribution math, renderer output, COLOR, persistence, database schema, cache lifetime or fingerprint
algorithms.
