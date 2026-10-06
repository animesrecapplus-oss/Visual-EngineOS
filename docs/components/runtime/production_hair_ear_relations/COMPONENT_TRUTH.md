# Component truth

Identity: `CMP-RUNTIME-PRODUCTION-HAIR-EAR-RELATIONS`.

Parent: `ProductionRenderSession.render_face`.
Children/dependencies: canonical Hair/Ear leaf adapter and canonical owner-geometry extractor.
Owner: `src/visual_engine/runtime/production_hair_ear_relations.py:20-59`.

Responsibility: resolve the real Hair → left Ear and Hair → right Ear production relations in stable order.

Non-responsibility: one-pair visibility semantics, geometry generation, camera transform, style resolution, renderer SVG,
Head/Ear relation, face-overlap relation, COLOR, cache lifetime, fingerprints, persistence and database.
