# Relations — CMP-EYE-GAZE

- `REL-GAZE-001`: semantic frame = EYEBALL / ocular assembly — VERIFIED by V1.83 hierarchy.
- `REL-GAZE-002`: aggregate parent = CMP-EYE — VERIFIED by eye public architecture.
- `REL-GAZE-003`: `Gaze` → `GazeSolver` — VERIFIED; solver consumes the value.
- `REL-GAZE-004`: `Gaze` → geometry builder — VERIFIED.
- `REL-GAZE-005`: `Gaze` → geometry transform — VERIFIED.
- `REL-GAZE-006`: `Gaze` → eye generator/cache-input projection — VERIFIED.
- `REL-GAZE-007`: `Gaze` → binocular pair path — VERIFIED through `BinocularGazeSolver`/pair construction.
- `REL-GAZE-008`: `Gaze` is not a Pupil semantic child — VERIFIED by V1.83 hierarchy.

No new parent, child, sibling or optical-physics relation is introduced.
