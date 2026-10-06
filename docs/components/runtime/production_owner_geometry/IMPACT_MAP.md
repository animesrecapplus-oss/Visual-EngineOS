# Impact map

Affected:
- `src/visual_engine/runtime/production_owner_geometry.py:1-67` — new owner.
- `src/visual_engine/runtime/production_face_render.py:29,84,90,93` — import and three real extraction consumers.
- `src/visual_engine/runtime/__init__.py:247-258` — public export.
- `src/visual_engine/runtime/production_face_overlap_visibility.py` — injected callable contract only; no algorithm change.
- `tests/unit/test_v160_production_face_overlap_visibility.py` — import migration.
- `tests/unit/test_v162_production_owner_geometry.py:1-80` — focused/hostile/integration tests.

Behavior-sensitive surfaces: camera owner geometry, depth values, path rebasing, visibility/occlusion inputs, SVG bytes and resolution-cache statistics.

Unaffected by design: geometry generation, transforms, appearance algorithms, renderer serialization, visibility algorithms,
COLOR semantics, persistence/database, cache lifetime and fingerprints.

`IMP-POG-001`: extraction changes ownership/import direction only; selected geometry/depth, SVG and cache behavior are identity-gated against V1.61.
