# Pupil dependencies and consumers

## Owner

`src/visual_engine/components/face/eyes/pupil/spec.py:9-31` — canonical PupilSpec owner.

## Real consumers

- `src/visual_engine/components/face/eyes/appearance/spec.py:12,17-26` — stores PupilSpec in EyeAppearance.
- `src/visual_engine/components/face/eyes/styles.py:9,31-32,63-64` — creates real style presets using PupilSpec.
- `src/visual_engine/components/face/eyes/generator.py:17,185-188,192-226` — consumes pupil values for geometry/cache inputs.
- `src/visual_engine/components/face/eyes/definitions.py:11` — compatibility import.
- `src/visual_engine/geometry/__init__.py:3-4,8-10` — public compatibility export through the eye facade.

## Dependencies

`pupil/spec.py:4-6` depends on the canonical PupilShape type, shared validation helpers and pupil effect value specs.

## Relation boundaries

Pupil↔Iris, Pupil↔Gaze, Pupil↔Eyelid and Pupil↔Transform remain relation records, not invented local consumers.
No database adapter or COLOR transformation consumes PupilSpec directly.
