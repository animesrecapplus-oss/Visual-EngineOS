# V1.87 — dependencies and consumers — CMP-EYE-EYEBROW

## Direct consumers — VERIFIED

- `components/face/eyes/appearance/spec.py:6,28` — composition owner stores `BrowSpec`.
- `components/face/eyes/styles.py:8,34,66` — authored presets construct `BrowSpec`.
- `components/face/eyes/expression.py:6,70-74` — expression solver derives a replacement value.
- `render/eye_svg_primitives.py:54-135` — production SVG brow renderer reads validated values.
- `components/face/eyes/definitions.py:17` — compatibility import.
- `geometry/__init__.py:3,8` — public compatibility export.

## Indirect consumers — VERIFIED

`EyeAppearance` carries the value into the eye SVG production path. Existing face/eye integration tests exercise
`EyeAppearance` with a brow. No additional consumer is promoted beyond traced source references.

## Dependencies — VERIFIED

Direct imports: Python `dataclasses`, `math`, `numbers.Real`, local `BrowStyle`, local `_color`.
No database, cache-policy or COLOR dependency is introduced.

## Cache/persistence

`_eye_cache_inputs` contains no eyebrow fields; this is an existing verified cache boundary. No `BrowSpec` migration or
persistence adapter was found in the current eight-file migration inventory.

## Unknowns intentionally not promoted

No independent eyebrow geometry owner, occlusion owner, morphology solver or resource ceiling is invented by V1.87.
