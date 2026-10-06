# Component truth

Identity: `CMP-FACE-HAIR-DEPTH`.

Parent: `CMP-FACE-HAIR`.

Children: none.

Owner: `src/visual_engine/components/face/hair.py:46-48`.

Responsibility: author `depth_layer=1` on the Hair surface.

Non-responsibility: calculating intersections, visibility, attribution, paint priority, morphology, material, COLOR, database schema or cache lifetime.

Reason for adoption: V1.57 geometry proves real Hair/Ear overlap, and the renderer already paints Hair after Ear. A coplanar depth contract would make semantic visibility disagree with the existing visual order.
