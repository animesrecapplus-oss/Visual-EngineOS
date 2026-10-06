# Component truth — CMP-FACE-HAIR

Identity: one `Hair` child owned by `HumanFace`.

Responsibility: emit one finite closed cap in component-local coordinates with
`HAIR` semantic region and explicit owner metadata.

Non-responsibility: strands, follicles, inner morphology, hair/ear occlusion,
accessories, expression deformation, material/light simulation, COLOR transforms,
cache lifetime, persistence schema and SVG policy.

Owner: `src/visual_engine/components/face/hair.py:1-61`.
Parent: `HumanFace` in `src/visual_engine/entities/face.py:4-74`.
Real downstream consumer: `face.human_with_eyes_nose_mouth_ears_hair` production
composite, then `ProductionRenderSession`.

Status is certified only for this bounded cap geometry, not for full hair anatomy.

## V1.58 change

`CMP-FACE-HAIR-DEPTH` is a child micro-component of this owner. `hair.py:46-48` now authors `depth_layer=1` so the certified Hair/Ear overlap has a semantic foreground relation consistent with the existing renderer paint order.
