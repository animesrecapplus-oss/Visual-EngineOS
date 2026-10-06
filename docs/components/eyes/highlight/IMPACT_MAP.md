# Impact map — V1.88 / CMP-EYE-HIGHLIGHT

- `IMP-HIGHLIGHT-001`: runtime change limited to `highlights/spec.py:1-35`.
- `IMP-HIGHLIGHT-002`: direct appearance/style/render/API consumers reviewed; no consumer implementation changed.
- `IMP-HIGHLIGHT-003`: pair appearance signature remains unchanged; valid tuple equality semantics remain intact.
- `IMP-HIGHLIGHT-004`: `_eye_cache_inputs` remains unchanged; no geometry cache invalidation change.
- `IMP-HIGHLIGHT-005`: no fingerprint/provenance/seed/FPS algorithm changed.
- `IMP-HIGHLIGHT-006`: no database migration or persistence representation changed; 8 migration files identical.
- `IMP-HIGHLIGHT-007`: no serialization contract changed beyond rejecting malformed constructor inputs earlier.
- `IMP-HIGHLIGHT-008`: valid renderer output is differential-tested against V1.87 for normal, all-shapes, boundary and hidden cases.
- `IMP-HIGHLIGHT-009`: API exports remain unchanged.
- `IMP-HIGHLIGHT-010`: component/geometry/integration/unit regression remains green after final source state.

Required unchanged behavior: valid shapes, valid numeric values, color validation, immutability, visibility behavior,
renderer output and geometry cache identity.
