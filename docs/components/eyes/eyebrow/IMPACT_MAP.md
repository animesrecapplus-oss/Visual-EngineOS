# V1.87 — impact map — CMP-EYE-EYEBROW

- `IMP-EYEBROW-001` source: only `eyebrow/spec.py` changed at runtime.
- `IMP-EYEBROW-002` tests: focused owner tests added; existing consumers re-executed.
- `IMP-EYEBROW-003` API: legacy and public exports unchanged.
- `IMP-EYEBROW-004` cache: `_eye_cache_inputs` unchanged; brow styling remains outside geometry identity.
- `IMP-EYEBROW-005` persistence: eight migration files unchanged; no database adapter identified.
- `IMP-EYEBROW-006` determinism: valid baseline SVG hashes unchanged across normal, rotation, hidden and boundary cases.
- `IMP-EYEBROW-007` performance: measured sanity delta only; no optimization introduced.
- `IMP-EYEBROW-008` hierarchy: eyebrow remains periocular sibling branch; no parent/child topology altered.
- `IMP-EYEBROW-009` COLOR: no COLOR code or transformation changed.
- `IMP-EYEBROW-010` rendering: valid production output remains byte-identical to V1.86 baseline in the tested cases.
