# Component truth — CMP-FACE-EAR-COMPOSITE

Identity: `CMP-FACE-EAR-COMPOSITE`.
Owner: `src/visual_engine/components/face/ear_composite.py`.
Parent: `HumanFace` production request.

Responsibility: compose the existing proven face-with-eyes/nose/mouth geometry with exactly two real Ear child geometries and expose deterministic dependency/cache inputs.

Non-responsibility: leaf ear geometry, eye/nose/mouth algorithms, renderer styling, occlusion algorithms, COLOR, persistence schema or cache lifetime.

Consumers: `production_face_geometry_registry.py` and `ProductionRenderSession` through the explicit default generator name.
