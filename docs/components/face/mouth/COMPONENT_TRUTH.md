# Component truth — CMP-FACE-MOUTH

## Identity

`CMP-FACE-MOUTH` = `components/face/mouth`; production child `HumanFace/mouth` of kind `Mouth`.

## Responsibility

`src/visual_engine/components/face/mouth.py:15-59` owns the renderer-neutral mouth geometry contract and its malformed width/height input boundary.
`src/visual_engine/components/face/mouth_composite.py:22-82` owns only the parent composite adapter.
`src/visual_engine/components/face/production_registry.py:10-14` owns production registry extension.

## Non-responsibility

No lip morphology system, expression solver, shading, material algorithm, COLOR transformation, database schema,
cache lifetime, renderer inference or general occlusion algorithm is owned here.

## Parent / children / siblings

Parent: `HumanFace` (`entities/face.py:4-36`). Children: none. Siblings: `Eye`, `Nose`, `Ear`, `Hair`.

## Status

`CERTIFIED` for V1.81 after the input-boundary hardening gate, hostile/integration tests, full regression,
visual invariance, dependency/source/database audits, documentation validation, purge and ZIP integrity.
