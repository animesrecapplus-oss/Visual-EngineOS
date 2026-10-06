# CMP-EYE-LASH — component truth

## Responsibility

Own immutable local value specifications for upper and lower lashes and reject malformed numeric input before those
values reach the aggregate appearance and renderer consumers.

## Non-responsibility

This component does not own eyelid geometry, lash placement, terminal exclusion, lash shadow rendering, visibility,
gaze/transform, style semantics beyond the existing vocabulary, COLOR transformations, cache identity/lifetime,
database schema, or renderer orchestration.

## Owner

`src/visual_engine/components/face/eyes/lashes/spec.py`.

- `LashSpec`: exact V1.85 lines recorded in `EVIDENCE.md`.
- `LowerLashSpec`: exact V1.85 lines recorded in `EVIDENCE.md`.

## Input boundary

Upper/lower lash authored values: booleans for enabled flags, finite real-valued morphology controls, integral count,
existing string colour and existing finite style/form vocabulary.

## Output boundary

Frozen `LashSpec` / `LowerLashSpec` value objects accepted by appearance, style/profile and render consumers.

## Authority

The spec module is authoritative only for local value validity. Geometry and visual topology remain downstream
owners.
