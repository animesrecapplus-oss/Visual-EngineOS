# Current status — V1.91

## V1.91 — HumanFace bilateral identity propagation correction

`CMP-FACE-EYE-BILATERAL` is `CERTIFIED` for the bounded existing HumanFace production identity contract.

### Implementation

- `left_eye` now reaches Eye geometry with `side="image_left"` in the existing HumanFace production path.
- `right_eye` remains `side="image_right"`.
- standalone/other Eye components remain `side="single"`.
- the unused `_eye_component_inputs` duplicate was removed from `face/generators.py`.
- `EYE_GEOMETRY_GENERATOR_VERSION` changed `9 → 10` because default geometry semantics changed.
- no Gaze, renderer, COLOR, DB migration or public export change.

### Validation

- V1.91 focused boundary/production suite: PASS.
- `tests/components` + `tests/integration`: PASS; one expected PostgreSQL skip; zero failures.
- compileall: PASS.
- dependency graph: 209 modules / 567 edges; 3 pre-existing SCCs; zero new SCCs; zero duplicate groups.
- DB migrations: 8 unchanged.
- cache identity: PASS; side is already part of `_eye_cache_inputs`.
- visual QA: four normal/boundary/interaction production cases produced; right-eye geometry unchanged and left-eye geometry changed exactly at the intended bilateral boundary; PNGs inspected.
- input-boundary diagnostic benchmark: +6.10% median in the measured workload; no optimization introduced.

The monolithic current full-suite run was attempted but exceeded the execution wall-clock limit. Therefore V1.91 does not claim a complete-current-suite PASS. V1.89's complete historical regression remains historical evidence only.

### Remaining gaps

- generic ocular aperture/depth/mask integration remains the next separately audited brick;
- generic prompt compiler/default camera semantic resolver remains planned;
- no universal `Component.side` contract is promoted.

Git remains `NOT_APPLICABLE` because the project is not a Git repository.
