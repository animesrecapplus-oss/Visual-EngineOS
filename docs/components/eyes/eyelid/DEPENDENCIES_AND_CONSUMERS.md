# CMP-EYE-EYELID — dependencies and consumers

## Verified direct consumers

- `components/face/eyes/appearance/spec.py:4,20` — stores `EyelidAppearance`.
- `components/face/eyes/generator.py:15,217-222` — imports and projects selected eyelid values into geometry-cache inputs.
- `render/eye_svg_contours.py:120-136` — consumes lid widths, colors, enable flags, styles and opacity.
- `render/eye_svg_effects.py:147-162` — consumes crease enable flags, widths, color and opacity.
- `components/face/eyes/definitions.py:14` — compatibility import/export.
- `components/face/eyes/eyelid/__init__.py:1-2` — domain export.
- `geometry/__init__.py:3,9` — compatibility public export.

## Dependencies

- `dataclasses` for frozen value semantics;
- `numbers.Real` and `math.isfinite` for non-coercive finite numeric validation;
- `contracts.validation._color` for existing color validation;
- `contracts.types.ContourStyle` for the existing style vocabulary.

## Cache / persistence

Selected eyelid geometry controls are already represented in `_eye_cache_inputs`; visual-only values are deliberately
outside the geometry cache key. V1.86 changes no cache algorithm or identity. No direct database adapter or migration
for `EyelidAppearance` is verified; no database change is made.
