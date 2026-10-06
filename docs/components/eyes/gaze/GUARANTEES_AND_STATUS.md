# Guarantees and status — CMP-EYE-GAZE

Status: `CERTIFIED` only for the V1.89 `Gaze` authored-input boundary.

Certified guarantees:
- authored numeric fields are strict finite non-bool Reals;
- target is `None` or an immutable finite numeric pair;
- direction vocabulary is closed;
- existing non-negative magnitude rules remain;
- valid vector semantics are preserved;
- cache/persistence/renderer algorithms are unchanged.

Not certified by V1.89:
- artistic gaze quality;
- 3D side/back gaze physical correctness;
- optical/biological realism;
- binocular convergence quality beyond existing tests;
- pupil containment beyond existing solver contracts;
- new prompt semantics;
- cache lifetime/performance ceilings;
- live PostgreSQL execution.
