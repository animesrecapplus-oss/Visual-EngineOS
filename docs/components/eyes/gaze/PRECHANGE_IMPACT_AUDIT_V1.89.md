# Pre-change impact audit — V1.89 Gaze

## Baseline

V1.88 certified ZIP SHA-256: `b8ea6fdab743097d5d2740942f5e9c0f5fe26cdc58347168f05f5ed67544486e`.

Owner before change: `gaze/solver.py:26-52`, SHA-256
`d5e051c3fa8c2a2970c7ade7364f0e6933c3477d030fc4c1796f4771c29c8851`.

## Verified defects

`Gaze(x=True)`, `Gaze(x="0.5")`, target elements containing bool/string values and list targets were accepted.
`Gaze(x=10**10000)` and a huge target element could leak `OverflowError` during float conversion.
These are constructor-boundary defects, not solver algorithm defects.

## Impact dimensions

- Files: owner + focused tests + V1.89 truth/governance/evidence files.
- Direct consumers: geometry builder, transform, generator, pair path, compatibility exports.
- Indirect: eye geometry and production SVG path.
- Parent: CMP-EYE / EYEBALL ocular assembly relation; no parent behavior changed.
- Children: none promoted.
- Siblings: no changes.
- Cache: Gaze remains in `_eye_cache_inputs`; valid identity must remain identical.
- Fingerprint: no algorithm/version change authorized.
- Persistence: no Gaze DB representation or migration consumer verified; no change.
- Serialization: public exports unchanged; no serialized Gaze record identified.
- Determinism: valid vector outputs unchanged.
- Seed/FPS/time: not applicable to this immutable constructor boundary.
- Visual: valid render must remain identical; malformed values must never reach rendering.
- API: valid existing constructor calls preserved; malformed inputs now fail earlier.
- Production path: no solver or renderer algorithm change.

## Stop/re-evaluate event

Initial local edit removed `_finite` from imports. Consumer integration immediately exposed that `BinocularGazeSolver`
still calls `_finite`. This was a newly verified dependency. The edit was stopped, the impact record updated,
and `_finite` was restored. The shared helper was not modified.
