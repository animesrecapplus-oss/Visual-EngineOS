# Decisions — V1.86

## DEC-V186-001 — select Eyelid horizontally

A fresh audit found a real executable owner with direct production consumers and reproducible local validation gaps.
Recent Iris/Pupil/Lash hardening bricks are deferred; planned anatomy is not promoted.

## DEC-V186-002 — local validation only

The existing owner already defines the numeric ranges. Add type/finiteness guards before those checks rather than
creating a shared abstraction or modifying geometry/rendering.

## DEC-V186-003 — no new anatomical contract

No eyelid proportions, maximums, occlusion semantics or topology are invented. Existing source evidence remains the
only local range authority.
