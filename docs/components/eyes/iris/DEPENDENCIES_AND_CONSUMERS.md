# Iris dependencies and consumers — V1.84

## Owner

`src/visual_engine/components/face/eyes/iris/spec.py:8-41` — canonical `IrisSpec` owner.

## Direct consumers / references

- `components/face/eyes/appearance/spec.py:9,16-37` — stores `IrisSpec` inside `EyeAppearance`.
- `components/face/eyes/styles.py:6,13-42,45-74` — constructs real production style presets.
- `components/face/eyes/generator.py:16,80-148,171-189,192-226` — reads iris shape for geometry contract output and cache inputs.
- `render/eye_svg_effects.py:22-24,166-192` — consumes IrisSpec visual values during SVG rendering.
- `components/face/eyes/pair.py:211-213` — derives a paired appearance by replacing iris colour.
- `components/face/eyes/definitions.py:13` — compatibility import.
- `visual_engine/geometry/__init__.py:4,9` — public compatibility export.

## Dependencies

`iris/spec.py` depends directly on the shared `IrisShape` vocabulary and shared `_color` validator.

## Cache / persistence boundary

`generator.py:_eye_cache_inputs` includes `iris_shape` but deliberately excludes iris visual fields such as colour,
opacity, pattern, rings and glow. V1.84 does not alter cache selection or cache lifetime.

No IrisSpec database representation or migration was found in the verified source tree. No persistence change is
authorized by this brick.
