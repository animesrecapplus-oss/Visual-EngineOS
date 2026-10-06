# Impact map

Affected:
- `src/visual_engine/runtime/production_visual_styles.py:1-66` — new owner.
- `src/visual_engine/runtime/production_face_render.py:31,78-81` — import and existing production consumer.
- `src/visual_engine/runtime/__init__.py:247-258` — public export.
- `tests/unit/test_v161_production_visual_styles.py:1-126` — focused/hostile/integration tests.

Behavior-sensitive surfaces:
- resolution cache hit/miss/store counts;
- visual context/version/fingerprint delegation;
- SVG style lookup and owner ordering;
- production Hair/Ear/Head/Ear occlusion inputs.

Unaffected by design:
- generic appearance algorithms;
- geometry generators/transforms;
- renderer serialization algorithm;
- occlusion/visibility algorithms;
- database/persistence;
- COLOR semantics;
- cache lifetime/ownership.

`IMP-PVS-001`: extraction changes module ownership and imports only; behavior-sensitive resolution, cache and renderer inputs
are explicitly preserved and tested against V1.60.
