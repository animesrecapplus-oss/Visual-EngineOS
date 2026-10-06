# Current status — V1.87

## V1.87 — Eyebrow local input-boundary hardening

`CMP-EYE-EYEBROW` is `IMPLEMENTED / VALIDATED` for the documented `BrowSpec` local boolean/type/finiteness scope.

Canonical owner: `src/visual_engine/components/face/eyes/eyebrow/spec.py:8-53`.
Semantic parent: `ORBIT / PERIOCULAR`; aggregate/public parent: `CMP-EYE`.

### Implementation

- strict boolean `enabled` validation;
- finite `Real`, non-bool validation for all local numeric fields;
- explicit handling of float-conversion overflow during finiteness validation;
- existing ranges, style vocabulary, color validation and immutability preserved;
- no geometry, placement, cache algorithm, visibility, COLOR or database algorithm change.

### Evidence

- focused V1.87 suite: 72/72 PASS;
- components: 359 PASS;
- integration: 5 PASS with the expected PostgreSQL skip when DSN is absent;
- unit: 1079 PASS in five execution chunks;
- total collected tests: 1443;
- compileall PASS;
- 209 modules / 567 edges; 3 pre-existing SCCs, 0 new SCCs, 0 duplicate groups;
- 8 DB migrations unchanged;
- five valid visual differential cases have identical SVG SHA-256 values to V1.86; PNGs generated and inspected;
- benchmark is sanity-only, median delta +6.4807%, no optimization claim.

Git is intentionally not part of the gate because the project is not a Git repository.

### Status

`CERTIFIED` for the documented local `BrowSpec` input-boundary scope. Git is not applicable to this non-Git project.
