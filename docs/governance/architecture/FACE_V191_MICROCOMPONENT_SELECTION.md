# V1.91 — HumanFace bilateral identity propagation selection

## VERIFY

Baseline: exact V1.89 certified source/checkpoint. V1.90 is audit-only and records no runtime change.
The V1.90 traceability matrix classifies HumanFace bilateral propagation as `CONFLICT/DEFECT` and explicitly selects it as the next concrete runtime brick.

Fresh executable reproduction against V1.89:
- `left_eye` default geometry: inner canthus `(-0.39, 0)`, outer `(-0.17, 0)` — wrong for the existing `image_left` convention.
- explicit `image_left`: inner `(-0.17, 0)`, outer `(-0.39, 0)` — expected.
- `right_eye` default already matches `image_right` because its symmetric default geometry is not sensitive to the missing mirror flag.

## IDENTIFY

Selected micro-component: `CMP-FACE-EYE-BILATERAL`.
Canonical input owner: `src/visual_engine/components/face/eyes/generator.py`.
HumanFace identity source: `src/visual_engine/entities/face.py:19-21`.
Production orchestration: `src/visual_engine/runtime/generation.py:51-84`.

## ARCHITECT

Responsibility: preserve the existing HumanFace bilateral identity at the Eye default-input boundary.
Non-responsibility: Gaze, camera, coordinate inference, renderer, clipping/mask, COLOR, DB, prompt compiler.

## DECISION

Use the existing stable HumanFace child IDs `left_eye` / `right_eye` as the bounded production identity source.
Do not infer side from coordinates and do not introduce a generic `Component.side` field.
Remove the unused duplicate `_eye_component_inputs` helper rather than maintaining two side-resolution boundaries.

## AUTHORIZED CHANGE

- Eye default input side resolution;
- Eye generator version `9 → 10`;
- stale unused helper removal;
- focused/adversarial/production/visual tests;
- truth dossier and governance/evidence.

The following brick remains separate: generic ocular aperture/depth/mask integration.
