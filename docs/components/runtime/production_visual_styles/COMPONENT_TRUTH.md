# Component truth

Identity: `CMP-RUNTIME-PRODUCTION-VISUAL-STYLES`.

Parent: production render session/style boundary.
Children: none.
Siblings: production face-overlap visibility; Hair/Ear; Head/Ear; pair occlusion.
Owner: `src/visual_engine/runtime/production_visual_styles.py:18-66`.

Responsibility: own the existing production style-map construction for geometry owners that reach the SVG renderer.

Non-responsibility: generic appearance resolution, geometry generation/transform, SVG serialization, occlusion algorithms,
cache lifetime, persistence/database, COLOR domain semantics, or component topology.

The root visual is injected from the session's already-computed `ResolvedComponent`; child-owner visuals delegate to the
canonical resolver. This preserves one resolution/cache lookup per owner.
