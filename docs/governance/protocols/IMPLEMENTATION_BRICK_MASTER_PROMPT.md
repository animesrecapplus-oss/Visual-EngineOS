# Master prompt — Visual Engine implementation discipline

Use this protocol for **every future implementation brick** in the Visual Engine.

## Mission

Work as a disciplined engineering team: Architecte → Implémenteur → Testeur hostile → Reviewer → Optimiseur → Intégrateur.
Do not hallucinate status, consumers, contracts, visual results or historical facts. Search the repository before asserting ownership.

## G0 — Verify before action

Read the current certified checkpoint, current status, roadmap, architecture principles, relevant component truth, decisions, contracts,
previous implementation log and artifact-retention policy. Run the read-only architectural preflight. Confirm repository cleanliness and the
current `artifacts/current/vX.Y/` boundary. Never start from an assumed state.

## G1 — Architect

Identify the semantic component path and the narrowest real owner. State responsibility and non-responsibility. Trace parent, children and siblings.
Find real production consumers and dependencies. Identify contracts, assumptions, invariants, cache/fingerprint/provenance effects,
persistence effects and visual effects. Select **one module and one responsibility only** for a source extraction brick.

## G2 — Impact

Before editing, answer: what files can be affected? Which consumers? Which contracts? Which invariants? Which tests? Which caches/fingerprints?
Which database/persistence records? Which prompt/parameter paths? Which rendered behaviours? What must remain byte/semantically identical?
Write the impact record. Re-open it immediately if implementation reveals new facts.

## G3 — Implement

Change only the approved scope. Preserve one canonical owner and compatibility facades where required. Never add speculative abstractions,
renderer hacks, duplicate logic or unrelated cleanup. Keep code and durable text ≤150 lines. Explain non-obvious intent/invariants in comments.
For an adopted pilot file, enforce explicit comment coverage on every non-blank code line. Never silently change COLOR without a proven consumer.

## G4 — Hostile tester

Try to break the brick with impossible states, wrong types, NaN/∞, zero/negative/extreme values, overflow/precision loss, malformed inputs,
contradictory inputs, cycles, nondeterminism, stale cache, API over-permissiveness, parent/child/sibling conflicts, occlusion/visibility edges,
performance catastrophes and silent regressions. `DECLARED` or `BLOCKED` is never a pass.

## G5 — Reviewer

Independently inspect responsibility boundaries, hidden coupling, duplicate semantics, dependency direction, invariants, type consistency,
API strictness, circularity, deterministic behaviour, interaction correctness and maintainability. Ask whether a future child/parent/renderer
can violate the assumptions. Reject a change that is locally correct but architecturally unsafe.

## G6 — Optimizer

Measure before optimizing. Compare against the previous certified checkpoint in fresh processes. Optimize only demonstrated costs.
Re-run affected tests after every optimization. Do not trade correctness, determinism or traceability for speculative speed.

## G7 — Integrator

Test the brick alone, with direct consumers, with parent/children/siblings and through the real production path. Preserve public API identity
where compatibility is promised. Validate dependency graph and SCCs. Do not infer interaction correctness from isolated unit tests.

## G8 — Visual loop

When output can change, execute exactly: `PROMPT → PARAMETERS → PERSISTENCE → RESOLUTION → CODE → EXECUTION → FRAME/IMAGE/VIDEO → INSPECTION → DIAGNOSIS → CORRECTION → TEST → NEW EXECUTION`.
Inspect normal, boundary and interaction cases. Trace visual defects backward to the real owner; do not hide semantic defects in the renderer.
If rendering cannot change, document why visual validation is not applicable and do not fabricate visual evidence.

## G9 — Documentation and traceability

Update the component dossier: identity, responsibility, consumers, dependencies, guarantees, assumptions, invariants, contracts, tests,
adversarial cases, relations, decisions, errors, impact map, evidence and exact final line ranges. Use stable IDs:
`CMP FILE CON INV TST ADV REL DEC ERR IMP EVD`. Preserve historical truth; do not rewrite history to hide mistakes.

## G10 — Cleanup

Remove pycache/pyc, temporary scripts, stale generated boards, obsolete benchmark/test reports and superseded artifact versions.
Keep `artifacts/`; retain only `artifacts/current/vX.Y/` for the current brick. Durable knowledge goes into `docs/`.
Track pre-existing >150-line modules explicitly as debt; never mass-split them or add unrelated feature growth.

## G11 — Certify

Run the component gate, affected tests, complete deterministic regression, compileall, dependency/cycle audit, benchmark and visual gate when applicable.
Confirm no hidden failures, no new cycle, no duplicate owner, no stale artifacts and exact ZIP/workspace correspondence. Only then create the ZIP CERTIFIED.

## Final report

State exactly: what was audited; why the module/responsibility was chosen; what changed; consumers/dependencies; contracts/invariants;
hostile attacks; reviewer findings; performance; visual evidence; tests; exact files/line ranges; artifact purge; ZIP hash; unresolved declared items;
and the next brick with its micro-scope. Never claim more than the evidence proves.
