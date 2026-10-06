# Evidence — CMP-EYE-GAZE V1.89

- `EVD-GAZE-001`: exact V1.88 baseline package; ZIP SHA `b8ea6fdab743097d5d2740942f5e9c0f5fe26cdc58347168f05f5ed67544486e`.
- `EVD-GAZE-002`: pre-change owner `gaze/solver.py:26-52`; baseline SHA recorded in pre-change audit.
- `EVD-GAZE-003`: fresh hostile probe reproduced bool/string acceptance and huge-integer `OverflowError`.
- `EVD-GAZE-004`: V1.89 owner implementation = `gaze/solver.py:45-80`, SHA `685f65e75ad400b4ca03d140f8db2ba7fd7def78481f8de5dac36e49536ecc07`, recorded by final line-range artifact.
- `EVD-GAZE-005`: focused `TST/ADV-GAZE` suite PASS.
- `EVD-GAZE-006`: direct/indirect consumer regression PASS.
- `EVD-GAZE-007`: dependency graph, SCC and duplicate audit PASS.
- `EVD-GAZE-008`: database migration identity unchanged.
- `EVD-GAZE-009`: valid-value cache identity unchanged.
- `EVD-GAZE-010`: visual normal/boundary/interaction differential evidence produced and inspected.

Every final file line range is tied to the V1.89 source snapshot; no V1.88 range is used as V1.89 proof.
- `EVD-GAZE-011`: benchmark `BASELINE` vs `MEASURED RESULT`; local validation optimization reduced the measured delta from +135.898% to +89.357% versus V1.88.
- `EVD-GAZE-012`: visual contract comparison `EXPECTED VISUAL STATE = valid V1.88 render unchanged`; `ACTUAL VISUAL STATE = identical SVG hashes in normal, boundary and interaction cases`; PNGs manually inspected.
