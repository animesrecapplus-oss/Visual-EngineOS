# Test status

`tests/unit/test_v160_production_face_overlap_visibility.py:22-76`: 5/5 focused extraction/hostile tests PASS.

Compatibility matrix V1.47/V1.55/V1.56/V1.57/V1.58/V1.59 plus V1.60 extraction: PASS.

Behavior identity evidence compares the certified V1.59 checkpoint with V1.60: SVG SHA-256, camera geometry digest,
geometry cache key and visibility/attribution values are identical.

Full regression inventory: 132 test files / 1069 tests / 1068 PASS / 1 expected PostgreSQL skip / 0 FAIL, executed as eight isolated deterministic groups because the monolithic command exceeded the execution window. Compileall PASS.
