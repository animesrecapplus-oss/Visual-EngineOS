# Current status — V1.85

## V1.85 — Lash local input-boundary hardening

`CMP-EYE-LASH` is `CERTIFIED` for its local `LashSpec` / `LowerLashSpec` numeric/type validation scope.

Canonical owner: `src/visual_engine/components/face/eyes/lashes/spec.py:1-85`.
Semantic parent: `ORBIT / PERIOCULAR`. Aggregate/public parent: `CMP-EYE`.

### Implemented

- strict boolean `enabled` validation;
- strict finite `Real` validation for lash numeric controls;
- strict integral, non-bool `count` validation;
- existing ranges, style/form vocabulary and colour validation preserved;
- no renderer, geometry, cache, COLOR or database algorithm change.

### Evidence

- 1278 tests collected: 1277 PASS, 1 expected PostgreSQL SKIP, 0 FAIL;
- compileall PASS;
- 209 modules / 567 edges; 3 pre-existing SCCs, 0 new SCCs, 0 duplicate groups;
- 8 DB migrations unchanged;
- production SVG hashes identical to V1.84 for front, +12°, -12° and hidden cases;
- actual front PNG produced and inspected;
- benchmark is sanity-only, median delta +0.81%, no optimization claim.

Git is intentionally not part of the gate because the project is not a Git repository.

### Remaining frontier

No resource ceiling, deeper lash anatomy or visual calibration is promoted by V1.85. The next brick must again be
selected through a fresh horizontal audit.
