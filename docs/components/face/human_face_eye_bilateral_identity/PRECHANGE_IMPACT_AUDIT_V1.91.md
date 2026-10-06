# V1.91 pre-change impact audit — CMP-FACE-EYE-BILATERAL

## VERIFY

Starting checkpoint: exact V1.89 certified package. V1.90 is audit-only/no-runtime-change and explicitly selects HumanFace→Eye bilateral propagation as the next runtime brick.

Fresh reproduction against V1.89 confirmed the left HumanFace Eye defaulted to `single`, reversing its medial/lateral canthus semantics. The canonical EyePair path already passes `image_left` / `image_right` explicitly.

## IDENTIFY

Canonical default-input owner: `src/visual_engine/components/face/eyes/generator.py`.
HumanFace authoring identity: `src/visual_engine/entities/face.py:19-21`.
Production generation orchestration: `src/visual_engine/runtime/generation.py:51-84`.

## AUTHORIZED

- correct bounded HumanFace `left_eye` / `right_eye` side propagation;
- remove the unused stale duplicate `_eye_component_inputs` helper;
- bump Eye geometry generator version because default geometry semantics change;
- add focused/adversarial/production/visual evidence and truth documentation.

## FORBIDDEN

No Gaze change; no renderer clipping/mask change; no COLOR change; no DB/migration change; no generic Component side field; no coordinate inference; no prompt compiler.

## IMPACT

Side already participates in `_eye_cache_inputs`, so corrected side changes geometry identity without changing the cache algorithm. No migration or public export change is required.
