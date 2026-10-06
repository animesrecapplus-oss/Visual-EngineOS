# CMP-EYE-LASH — dependencies and consumers

## Verified direct consumers

- `src/visual_engine/components/face/eyes/appearance/spec.py` — stores upper/lower lash specs.
- `src/visual_engine/components/face/eyes/styles.py` — constructs authored presets.
- `src/visual_engine/components/face/eyes/profiles.py` — transforms lash density/length through `replace`.
- `src/visual_engine/render/eye_svg_primitives.py` — renders upper lashes and iterates `count`.
- `src/visual_engine/render/eye_svg_effects.py` — renders lower lashes and iterates `count`.
- `src/visual_engine/components/face/eyes/definitions.py` — compatibility import/export.
- `src/visual_engine/components/face/eyes/lashes/__init__.py` — public lash-domain export.
- `src/visual_engine/geometry/__init__.py` — compatibility public export.

## Verified dependencies

- `dataclasses` for immutable value objects.
- `numbers.Integral` / `numbers.Real` for non-coercive numeric type validation.
- `math.isfinite` for finite numeric state.
- `contracts.validation._color` for existing colour validation.
- `contracts.types` for existing style/form vocabulary.

## Indirect/system relations

Lashes consume resolved eye geometry and visibility at render time. The production renderer owns emission and terminal
exclusion. No new dependency is introduced by V1.85.

## Database

No direct LashSpec persistence adapter or migration is verified. No database change is made.
