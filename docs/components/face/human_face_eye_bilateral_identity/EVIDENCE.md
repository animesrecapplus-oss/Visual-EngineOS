# Evidence — CMP-FACE-EYE-BILATERAL V1.91

- `EVD-FEB-001`: exact V1.89 certified baseline ZIP, SHA `9976b39d9e8a569bae7fe74176f9f0c023c9370947fd50b6f7652da3168b7a2c`.
- `EVD-FEB-002`: V1.90 executable reproduction: HumanFace left Eye default anchors were `inner=(-0.39,0)` and `outer=(-0.17,0)`; canonical `image_left` reverses them.
- `EVD-FEB-003`: final owner mapping at `generator.py:156-171`, V1.91.
- `EVD-FEB-004`: `EYE_GEOMETRY_GENERATOR_VERSION=10` at `generator.py:22-23`.
- `EVD-FEB-005`: focused V1.91 suite passed 5/5; affected ocular/production suites also passed.
- `EVD-FEB-006`: `tests/integration` + `tests/components` passed with one expected PostgreSQL skip and zero failures.
- `EVD-FEB-007`: dependency graph remained 209 modules / 567 edges / 3 pre-existing SCCs / 0 new / 0 duplicate groups.
- `EVD-FEB-008`: 8 DB migrations unchanged.
- `EVD-FEB-009`: V1.91 visual QA produced 4 baseline/current cases; right-eye owner hashes stayed identical while left-eye owner hashes changed as expected; PNG comparisons were inspected.
- `EVD-FEB-010`: cache identity audit passed; side is explicitly present in `_eye_cache_inputs` and left/right default identities differ.

The full monolithic current test suite was attempted but exceeded the execution wall-clock limit; therefore no complete-current-suite PASS claim is made. V1.89 full regression evidence remains historical baseline evidence only.
