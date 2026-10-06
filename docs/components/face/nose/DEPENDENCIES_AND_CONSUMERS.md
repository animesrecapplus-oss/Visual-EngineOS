# Dependencies and consumers — CMP-FACE-NOSE-001

Dependencies:
- `GeometryContract`, `GeometryPath`, `GeometrySurface`;
- `Component` and existing parameter/anchor contract;
- `RegisteredGeometryGenerator`;
- existing face production composites and generic cache/resolution path.

Real consumers:
- `src/visual_engine/components/face/generators.py:309-314` selects the Nose child for the face-with-eyes-nose family;
- `src/visual_engine/components/face/mouth_composite.py:31-68` consumes Nose in the Mouth-inclusive composition;
- `src/visual_engine/components/face/ear_composite.py` consumes that production base;
- `src/visual_engine/components/face/hair_composite.py` consumes the ear-inclusive base;
- production rendering reaches the final composite through `ProductionRenderSession`.

Database: no Nose-specific migration or SQL consumer verified.
COLOR: no Nose-specific transformation consumer verified.
