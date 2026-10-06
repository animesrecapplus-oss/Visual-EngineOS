# A0 closure audit — 2026-09-15

## Scope
Targeted second audit of the A0 structural closure tranche. This verifies `RuntimeGraph`,
PostgreSQL migration/persistence lifecycle, and the eyebrow/closed-eye defect. It is **not**
the planned A10 project-wide audit.

## Results

| Gate | Result |
|---|---|
| A0 `global_visible` correction retained | PASS |
| coverage delegates to authoritative visibility semantics | PASS |
| RuntimeGraph topology mutation is detected | PASS |
| RuntimeGraph indexes are immutable | PASS |
| RuntimeGraph explicit rebuild lifecycle | PASS |
| PostgreSQL migration ordering/idempotence | PASS |
| PostgreSQL migration ledger (`schema_versions`) | PASS |
| PostgreSQL gap/unknown-version refusal | PASS |
| PostgreSQL entity write/read transaction path | PASS |
| Live PostgreSQL round trip | SKIPPED — explicit `VISUAL_ENGINE_POSTGRES_DSN` required |
| Brow/closed-eye stable reference frame | PASS |
| Brow gap hard bound | PASS |
| Visual artifact regeneration | PASS — two identical manifests |
| A3 fingerprint closure | OPEN |
| A4 documentation reconciliation | OPEN |
| A5 complete QA restoration | OPEN |
| A6 version stabilization | OPEN |
| A8 generic E2E | OPEN |
| A9 adversarial/property suite | OPEN |
| A10 final audit | OPEN |

## RuntimeGraph

The prior lifecycle ambiguity is closed for topology. `RuntimeGraph` is a compiled view over the
authoring tree, with immutable mapping/tuple indexes. A deterministic digest covers component
IDs, kinds, parents, child ordering, and relation endpoints/types. If this topology changes,
queries fail closed and `rebuild()` is the explicit transition to a new graph.

The graph deliberately does not become an owning mutable copy of `Component`, and it does not
silently synchronize itself. Local visual/geometry mutation remains under content fingerprint
and cache contracts.

## PostgreSQL

An explicit migration runner now discovers `db/migrations/*.sql` in deterministic order, records
applied versions in `schema_versions`, executes missing migrations transactionally, and refuses
gapped or unknown histories. `PostgresEntityRepository` exposes explicit `migrate()` and
`current_schema_version()` operations and commits entity writes.

The live PostgreSQL test is correctly skipped when no DSN is supplied. No live-server success is
claimed in this environment.

## Eyebrow / closed eye

The visual defect was traced to using state-dependent `visible_height` as the brow reference.
A closed eye has zero aperture height, so that reference collapsed and pulled the brow toward the
lid. The fix derives a stable full-opening reference from the same eye morphology and upper lid
fold. The brow gap is then solved in that frame and re-bounded after gaze coupling.

`artifacts/qa_v13_a0_closure/brow_normal.png`, `brow_closed.png`, and `brow_covered.png` were
visually inspected. Two consecutive executions of `tools/qa_a0_closure.py` produced identical
SHA-256 manifests.

## Residual findings

- Live PostgreSQL verification still requires a real server/DSN.
- A3–A10 remain independent gates and are not silently marked complete.
- Historical documentation still contains duplicate decision IDs and historical stale checkboxes;
  those belong to A4 and were not silently rewritten here.
- Deep ocular artistic/anatomical systems remain future work; this closure does not claim the eye
  subsystem is production-complete.

## Re-audit 2 supersession note — 2026-09-15

This document's earlier PostgreSQL migration conclusion is superseded by
`docs/runtime/foundations/V1.3_A0_STRUCTURAL_CLOSURE_REAUDIT_2026-09-15__part_01.md` (split document; see adjacent parts). A second audit found that the previous
runner could record migration `001` without executing its SQL, and the original fake-cursor test
did not catch that defect. The runner and tests have been corrected. Live PostgreSQL remains
unverified until a real server/DSN is supplied.
