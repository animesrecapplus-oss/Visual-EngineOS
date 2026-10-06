# CMP-EYE-EYELID — component truth

## Responsibility

Own immutable local `EyelidAppearance` values and reject malformed boolean/numeric input before appearance,
geometry and render consumers use those values.

## Non-responsibility

Does not own eyelid geometry, aperture topology, globe coupling, canthus construction, lash placement, visibility,
gaze/transform, COLOR transforms, cache lifetime/algorithm, database schema or renderer orchestration.

## Owner

`src/visual_engine/components/face/eyes/eyelid/spec.py:8-73`.

## Input boundary

Four boolean enable controls; twelve finite real-valued appearance controls; existing optional/required colors;
existing contour-style vocabulary.

## Output boundary

Frozen `EyelidAppearance` value consumed by the existing eye appearance, geometry and SVG render paths.

## Authority

The owner is authoritative only for local value validity. Geometry, visibility, cache and rendering remain downstream
owners.
