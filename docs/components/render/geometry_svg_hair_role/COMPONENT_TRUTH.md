# Component truth — CMP-RENDER-GEOMETRY-SVG-HAIR-ROLE

Identity: minimal generic SVG role required by V1.57 Hair geometry.
Responsibility: recognize `hair` as a closed filled role and paint it at deterministic priority 5.
Non-responsibility: Hair geometry generation, visibility resolution, occlusion calculation,
COLOR transformation, material simulation and persistence.
Owner: `src/visual_engine/render/geometry_svg.py:45-63, 197-211`.
