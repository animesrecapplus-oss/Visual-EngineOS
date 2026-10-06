# Impact map — CMP-FACE-EYE-BILATERAL V1.91

- `IMP-FEB-001`: Eye default input construction changes only its derived `side` field for the bounded HumanFace identities.
- `IMP-FEB-002`: `face/generators.py` removes an unused duplicate `_eye_component_inputs` boundary; no verified runtime caller existed.
- `IMP-FEB-003`: Eye generator version changes `9 → 10` because default geometry semantics changed.
- `IMP-FEB-004`: existing `_eye_cache_inputs` already includes `side`; cache identity therefore differentiates corrected inputs.
- `IMP-FEB-005`: EyePair explicit `image_left`/`image_right` path remains unchanged.
- `IMP-FEB-006`: Gaze solver, transforms, renderer algorithms and COLOR remain unchanged.
- `IMP-FEB-007`: no DB migrations or persistence schema change.
- `IMP-FEB-008`: public eye exports remain unchanged.
- `IMP-FEB-009`: valid right-eye geometry remains byte-equivalent in the V1.91 visual comparison; left-eye geometry changes as intended.
- `IMP-FEB-010`: production vertical slice must prove the corrected side reaches final SVG/PNG output.
