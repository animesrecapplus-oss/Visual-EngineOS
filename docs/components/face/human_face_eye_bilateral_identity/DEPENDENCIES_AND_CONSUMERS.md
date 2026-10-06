# Dependencies and consumers — CMP-FACE-EYE-BILATERAL

## Direct sources / owner

- `src/visual_engine/entities/face.py:19-21` — verified HumanFace child identity creation.
- `src/visual_engine/components/face/eyes/generator.py:156-171` — verified bounded side mapping.
- `src/visual_engine/components/face/eyes/generator.py:156-173` — verified default Eye input construction.
- `src/visual_engine/components/face/eyes/geometry/builder.py:38-40` — verified existing side semantics.

## Production consumers

- `runtime/generation.py:51-84` — resolves Eye child generators before HumanFace composition.
- `components/face/generators.py:107-165` — HumanFace eye-pair dependency/composition boundary.
- `components/face/mouth_composite.py`, `ear_composite.py`, `hair_composite.py` — indirect HumanFace composite consumers through child geometry.
- `runtime/production_face_render.py` / `ProductionRenderSession` — verified final production render path.

## Non-consumers
No Gaze ownership, renderer clipping ownership, COLOR transformation or DB migration consumer is introduced.
