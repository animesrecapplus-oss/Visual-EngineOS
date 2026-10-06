# Pre-change impact audit — V1.88

## Verified baseline

The V1.87 certified package was reopened by exact ZIP SHA-256 and its certified source was used as the baseline.
No Git state is required: this project is explicitly not a Git repository.

## Owner and boundary

`ReflectionMark` is the canonical executable owner at `highlights/spec.py:8-23` before change and `8-35` after change.
It validates only local authored value-object state.

## Defects reproduced before change

1. numeric strings accepted;
2. bools accepted as numeric values;
3. huge integer could leak `OverflowError`;
4. unknown shape accepted and routed to renderer fallback branch.

## Impacted surfaces

Direct consumers: `appearance/spec.py`, `styles.py`, `eye_svg_effects.py`, compatibility exports and pair appearance
signature. Indirect relation: appearance → renderer. Cache: reflection marks absent from `_eye_cache_inputs` and must
remain absent. Persistence: no migration representation identified; DB audit required. Visual: valid SVG must remain byte
identity-equivalent to V1.87. API: exports must remain unchanged.

## Authorized implementation

Only `src/visual_engine/components/face/eyes/highlights/spec.py` may change at runtime. Tests/tools/docs/artifacts may be
added for proof. Shared validation, renderer, cache, COLOR and database code are outside scope.
