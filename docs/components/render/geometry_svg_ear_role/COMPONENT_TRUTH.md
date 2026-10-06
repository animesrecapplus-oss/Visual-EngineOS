# Component truth — CMP-RENDER-GEOMETRY-SVG-EAR-ROLE

Owner: `src/visual_engine/render/geometry_svg.py`.

Responsibility: recognize semantic role `ear` as a closed filled path and give it deterministic paint precedence before `head` at the same non-negative depth.

Non-responsibility: geometry creation, visibility resolution, occlusion computation, appearance resolution, COLOR transformation or database persistence.

Consumer: V1.56 Ear production geometry only; existing roles remain unchanged.
