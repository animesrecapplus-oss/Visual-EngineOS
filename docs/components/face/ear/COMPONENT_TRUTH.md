# Component truth — CMP-FACE-EAR

## Identity

`CMP-FACE-EAR` is one direct `HumanFace` child of kind `Ear`; the production composite requires exactly two direct ears.

## Responsibility

`src/visual_engine/components/face/ear.py:15-61` owns renderer-neutral closed ear geometry, finite dimensions, local anchor and semantic `EAR` surface metadata. V1.80 additionally owns strict numeric validation when malformed component state bypasses the `Parameter` constructor boundary.

## Non-responsibility

No hair, inner-ear morphology, expression, material, lighting, COLOR transform, occlusion algorithm, renderer policy, cache lifetime or database schema is owned here.

## Owner / parent / siblings

Owner: `src/visual_engine/components/face/ear.py`.
Parent: `entities/face.py:35-42`.
Siblings: `Eye`, `Nose`, `Mouth`, `Hair`.

## V1.80 status

`IMPLEMENTED / TESTED / INTEGRATED / CERTIFIED`. Valid production geometry is unchanged; malformed numeric inputs now fail closed at the leaf boundary.
