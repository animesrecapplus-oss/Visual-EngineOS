# V1.82 pre-change impact audit — Pupil local specification boundary

## Scope

`CMP-EYE-PUPIL` is selected after a fresh V1.81 audit. This audit authorizes only the local
`PupilSpec` validation boundary in `pupil/spec.py`. Pupil geometry, gaze, iris containment,
eyelid exposure, renderer and COLOR remain outside scope.

## Verified defect

The current owner uses `_finite()` for a subset of numeric fields and does not include
`outline_width`. `_finite()` also coerces values with `float()`. Consequently a string can
survive in `x`, `y` or `rotation_deg`, while `NaN`/`+∞` can survive as `outline_width` and
boolean values are accepted as numeric state. These are malformed states under the existing
finite/typed contract.

## Impact

- Source owner: `src/visual_engine/components/face/eyes/pupil/spec.py:8-29`.
- Real consumers: `eyes/appearance/spec.py`, `eyes/styles.py`, `eyes/generator.py`, compatibility
  `geometry` export; exact ranges are recorded in the component dossier.
- Parent: `CMP-EYE`; child values: `PupilGlowSpec`, `PupilSmokeSpec` remain unchanged.
- Siblings: Iris, Eyelid, Gaze and Lashes are not modified.
- Contracts: `CON-PUPIL-001/002/003/005`; strengthen enforcement only, no new semantic field.
- Invariants: finite numeric state, positive scales, non-negative outline, bounded opacity,
  immutable value semantics.
- Cache/fingerprint: valid Pupil values and generator semantics remain unchanged; invalid values
  must never enter the valid cache path. No cache algorithm is changed.
- Persistence/database: PupilSpec is not a database schema owner; no DB change is authorized.
- Determinism: valid construction must remain value-identical.
- Visual behavior: valid Pupil geometry/appearance must remain unchanged. New hostile cases do not
  receive visual certification because they are rejected before rendering.

## Authorized implementation

1. Make `PupilSpec` reject bool/non-Real numeric inputs.
2. Include `outline_width` in finite validation.
3. Preserve all valid numeric values and existing public exports.
4. Add focused hostile tests only.

## Explicitly forbidden

No change to pupil geometry, gaze, iris relation, eyelid relation, renderer, COLOR, database,
cache policy, effects ownership or proposed Hair architecture.
