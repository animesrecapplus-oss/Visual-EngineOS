# Iris component truth — V1.84

Identity: `CMP-EYE-IRIS`.

Semantic parent: `EYEBALL` architectural node — VERIFIED by the V1.15 ocular depth contract. No standalone
executable `EYEBALL` owner is invented.

Aggregate/public parent: `CMP-EYE` — VERIFIED as the public eye aggregate.

Semantic child: `CMP-EYE-PUPIL` — VERIFIED by the V1.15/V1.17 contracts and the V1.83 hierarchy correction.

Owner: `src/visual_engine/components/face/eyes/iris/spec.py:8-41`.

Responsibility: validate immutable local IrisSpec values before aggregate, geometry and renderer consumption.

Non-responsibility: iris geometry generation, pupil containment/gaze, eyelid exposure, corneal optics, highlights,
renderer orchestration, cache lifetime, database schema, generic COLOR resolution, deeper iris morphology.

V1.84 closes only the local numeric/type boundary for counts and real-valued visual parameters. It does not claim
that every Iris blueprint atom is an implemented micro-component.
