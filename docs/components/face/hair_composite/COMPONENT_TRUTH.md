# Component truth — CMP-FACE-HAIR-COMPOSITE

Identity: one `Hair` child owned by `HumanFace`.

Responsibility: compose the certified V1.56 face-with-ears geometry with exactly one Hair child,
while carrying the Hair fingerprint into the composite cache identity.

Non-responsibility: Hair leaf geometry, strands, follicles, hair/ear occlusion,
accessories, expression deformation, material/light simulation, COLOR transforms,
cache lifetime, persistence schema and SVG policy.

Owner: `src/visual_engine/components/face/hair_composite.py:1-74`.
Parent: HumanFace production composition.
Real downstream consumer: `ProductionRenderSession.render_face` via the production registry.

Status is certified only for this bounded composition, not for full hair anatomy.
