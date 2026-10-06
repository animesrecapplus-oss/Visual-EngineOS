# Component truth

Identity: `CMP-RUNTIME-PRODUCTION-OWNER-GEOMETRY`.
Parent: production render/occlusion integration.
Children: none.
Siblings: production face-overlap visibility, production pair occlusion, Hair/Ear, Head/Ear, visual styles.
Owner: `src/visual_engine/runtime/production_owner_geometry.py:8-67`.

Responsibility: select one real geometry owner from camera-space surfaces/primitives, rebase selected path indices, and return its single authored depth layer.

Non-responsibility: geometry generation/transforms, appearance resolution, SVG serialization, visibility/occlusion algorithms,
cache lifetime, fingerprints, persistence/database, COLOR semantics, topology or anatomy.
