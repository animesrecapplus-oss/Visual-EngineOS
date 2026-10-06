# Component truth

Identity: `CMP-PROD-HAIR-EAR-OCCLUSION`.
Parent: production rendering runtime.
Children: none.
Owner: `src/visual_engine/runtime/production_hair_ear_occlusion.py:16-77`.

Responsibility: validate the real Hair/Ear owners and delegate their visibility/attribution relation to the canonical production pair owner.

Non-responsibility: generic pair validation, geometry generation, boolean geometry, depth algorithm, rendering, COLOR, database schema and cache lifetime.

V1.59 preserves the V1.58 Hair/Ear output contract while removing duplicated pair-resolution logic.
