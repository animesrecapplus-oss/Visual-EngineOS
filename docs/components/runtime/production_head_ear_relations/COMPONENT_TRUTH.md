# Component truth

Identity: `CMP-RUNTIME-PRODUCTION-HEAD-EAR-RELATIONS`.
Parent: `ProductionRenderSession.render_face`.
Children/dependencies: canonical Head/Ear leaf adapter and canonical owner-geometry extractor.
Owner: `src/visual_engine/runtime/production_head_ear_relations.py:18-65`.

Responsibility: resolve the existing Head → left Ear and Head → right Ear production relations in stable order.

Non-responsibility: one-pair visibility semantics, geometry generation, camera transform, style resolution, attribution, renderer SVG,
Hair/Ear relation, face-overlap relation, COLOR, cache lifetime, fingerprints, persistence and database.
