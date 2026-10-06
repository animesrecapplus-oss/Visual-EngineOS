# Component truth

Identity: `CMP-RUNTIME-VISIBILITY-DEPTH-RELATION`.
Owner: `src/visual_engine/runtime/visibility.py:254-259`.
Parent: generic visibility kernel.
Responsibility: preserve the actual nearest occluder `DepthRelation` in each resolved region.
Non-responsibility: deciding whether coplanar occlusion is allowed, geometry generation, renderer paint order, attribution or anatomy.
