# Component truth — CMP-EYE-HIGHLIGHT

## Identity

`CMP-EYE-HIGHLIGHT` owns the immutable `ReflectionMark` value object used for structured vector eye highlights.
Owner is verified at `src/visual_engine/components/face/eyes/highlights/spec.py:8-35`.

## Responsibility

Validate local authored shape, numeric and color input before downstream consumption while preserving the existing
value-object representation.

## Non-responsibility

No highlight placement solver, optical physics, iris geometry, gaze, eyelid exposure, visibility hierarchy,
renderer orchestration, COLOR transform, cache policy, persistence or new anatomy.

## Parent / relations

Aggregate parent `CMP-EYE` is VERIFIED. V1.83 classifies Highlight as a cross-relation ocular reflection system,
not a fixed Pupil child. Placement depends on resolved iris geometry in the renderer; this is a relation, not ownership.

## Lifecycle

Construction → immutable appearance/style/render use → destruction. No persistence lifecycle is verified.
