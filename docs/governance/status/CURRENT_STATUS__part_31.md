# Current status — V1.89

## V1.89 — Gaze local input-boundary hardening

`CMP-EYE-GAZE` is `CERTIFIED` for the documented `Gaze` authored-input boundary.

Canonical owner: `src/visual_engine/components/face/eyes/gaze/solver.py:45-80`, V1.89.
Gaze remains a cross-relation system controlling the internal ocular assembly; no new optical or 3D semantics were added.

### Implementation

- strict non-bool `Real` validation for authored numeric fields;
- finite-value checks with overflow/type failure handling;
- immutable two-value target tuple boundary;
- existing non-negative strength/amplitude rules preserved;
- existing direction vocabulary preserved;
- shared `_finite` retained for `BinocularGazeSolver` and not modified;
- solver, renderer, cache algorithm, COLOR and database semantics unchanged.

### Evidence

- focused: 46/46 PASS;
- components: 465 PASS;
- integration: 4 PASS + 1 expected PostgreSQL skip;
- unit: 1079 PASS in six deterministic chunks;
- total: 1549 collected, 1548 PASS, 1 expected PostgreSQL skip, 0 FAIL;
- compileall PASS;
- 209 modules / 567 edges; 3 pre-existing SCCs, 0 new, 0 duplicate groups;
- 8 DB migrations unchanged;
- Gaze remains a geometry cache input and valid cache keys differ when valid gaze differs;
- five visual differential cases have identical V1.88/V1.89 SVG SHA-256 values and PNGs were produced/inspected;
- benchmark: V1.89 measured +89.357% constructor median vs V1.88; no speculative optimization claim.

Git is `NOT_APPLICABLE` because the project is not a Git repository.

### Status

`CERTIFIED` for the local Gaze constructor boundary only. No artistic, optical-physics or new 3D gaze quality claim.
