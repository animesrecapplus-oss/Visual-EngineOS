# Dependencies and consumers — CMP-EYE-HIGHLIGHT

## Direct consumers / exposures

- `appearance/spec.py:8,33` imports and stores `ReflectionMark` (VERIFIED).
- `styles.py:10,37-72` constructs preset marks (VERIFIED).
- `render/eye_svg_effects.py:209-231` consumes mark fields for SVG rendering (VERIFIED).
- `definitions.py:18` preserves the compatibility export (VERIFIED).
- `geometry/__init__.py:4,9` exposes the compatibility API (VERIFIED).
- `pair.py:200-205` includes `reflection_marks` in appearance signatures (VERIFIED).

## Indirect relations

`ReflectionMark → EyeAppearance → render_eye_svg/_reflection_marks_svg` is VERIFIED.
`ReflectionMark → EyePair appearance signature` is VERIFIED.
`ReflectionMark → geometry cache identity` is intentionally absent: `_eye_cache_inputs` does not read reflection marks,
VERIFIED at `generator.py:192-226` and by V1.88 cache evidence.

No database consumer, migration or serialized persistent representation was found in the audited production path.
This absence is VERIFIED by the V1.88 database identity audit for migrations; a broader external persistence claim is
not made.
