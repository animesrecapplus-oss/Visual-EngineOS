# V1.87 — pre-change impact audit — CMP-EYE-EYEBROW

## Owner and responsibility

`src/visual_engine/components/face/eyes/eyebrow/spec.py:7-35` owns the immutable `BrowSpec` value boundary.
The change is limited to input type/finiteness validation. No geometry or placement algorithm is authorized.

## Direct consumers — VERIFIED

- `components/face/eyes/appearance/spec.py:6,28` stores `BrowSpec` in `EyeAppearance`.
- `components/face/eyes/styles.py:8,34,66` constructs authored presets.
- `components/face/eyes/expression.py:6,70-74` derives expression-adjusted brow values.
- `render/eye_svg_primitives.py:54-135` consumes brow values for SVG geometry/stroke output.
- `geometry/__init__.py:3,8` preserves the public compatibility export.
- `components/face/eyes/definitions.py:17` preserves the legacy export surface.

## Indirect/system relations — VERIFIED

`EyeAppearance` → renderer is the production path. Eyebrow is a periocular sibling branch, not an eyelid child.
`_eye_cache_inputs` deliberately excludes eyebrow styling because those values are presentation concerns; cache identity
must remain unchanged. No direct database adapter or migration consumes `BrowSpec`.

## Reproduced pre-change defects

- `BrowSpec(length=NaN)` accepted.
- `BrowSpec(length=+inf)` accepted.
- `BrowSpec(angle_deg=NaN)` accepted.
- `BrowSpec(x=+inf)` accepted.
- `BrowSpec(y=NaN)` accepted.
- `BrowSpec(enabled=1)` accepted.
- `BrowSpec(angle_deg='0.5')` accepted.
- `BrowSpec(min_eye_gap=10**10000)` raised `OverflowError` from local validation rather than a controlled invalid-input error.

## Impact — IMP-V187-001

Only the owner and its focused tests/dossier/governance evidence are expected to change. Existing valid values, style
vocabulary, color validation, hierarchy/rotation behavior, visibility, cache identity, persistence, API exports and
production rendering must remain unchanged.

## Persistence/cache/visual risk

No `BrowSpec` database schema or migration was found. No eyebrow field participates in `_eye_cache_inputs`. Rendering
can be affected by malformed inputs but must remain byte-identical for valid baseline cases.
