<!-- Refactored from docs/governance/roadmap/ROADMAP__part_01.md; source lines 930-1072; content preserved. -->
<!-- Part 8/16. Use the family index for navigation. -->
## V1.3 — A10 independent second full audit — 2026-09-16

**Status: implemented and verified offline; V1.3 is structurally closed within the explicitly verified
boundaries below. This is not a declaration of production rendering or live PostgreSQL completeness.**

A10 was audited before implementation and was not already closed. The existing A9 verifier was intentionally
not treated as the A10 audit: A10 checks cross-layer consistency, ownership, import topology, version/migration
drift, documentation contradictions, clean-package imports, prior-gate reproducibility, and the remaining
nonclaims.

### Independent findings and corrections

- Found a residual documentation contradiction in Phase 1: the roadmap prose said semantic-region foundations
  were implemented while the generic semantic-geometry checkbox still marked them wholly future. The checklist
  was split into an implemented **V1.3 semantic-region geometry foundation** and a still-planned production
  semantic-geometry layer.
- Found internal source modules still importing the historical `visual_engine.model` compatibility facade.
  Internal imports were routed to the canonical `components.common` ownership layer. The `model` package remains
  only a compatibility surface for existing callers/tests.
- Found a dependency-cycle risk in the stable-digest ownership: `versioning` depended on relation dependencies,
  while relation IDs depended back on `versioning`. The stable digest primitive was moved to the lower-level
  `runtime.identity` module; `versioning` retains the public compatibility export.
- Added an AST-based top-level import-cycle audit and a fresh-interpreter import smoke test across the complete
  package module set.
- Added cross-source checks for documentation status, package/engine version agreement, migration ordering,
  canonical model ownership, and deterministic A8 evidence reproducibility.

### A10 verification boundary

- A4, A5, A6, A7, A8 and A9 verifiers: **PASS**.
- Full `pytest`: **PASS**.
- `compileall` for source/tests: **PASS**.
- Top-level internal import graph: **acyclic**.
- Fresh import smoke: **PASS** for all discovered package modules.
- A8 evidence: identical SHA-256 across two consecutive verifier runs.
- Live PostgreSQL: **UNVERIFIED**; no live DSN/server was available.
- Package build: **NOT VERIFIED** because the build backend tooling was unavailable in this environment.
- Artistic/production rendering quality: **NOT CLAIMED**.
- Exhaustive fuzzing/formal verification: **NOT CLAIMED**.

### Structural closure decision

On the evidence available in this repository and environment, the V1.3 **structural hardening scope is closed**.
This means the architecture/contracts/implementation/tests/documentation/versioning/cache/persistence/renderer
boundaries audited by A0–A10 have a synchronized, deterministic, fail-closed baseline. It does **not** mean the
long-term visual engine is feature-complete: generic interaction/deformation, production color/lighting,
physically based optics, full 3D, production rendering quality, prompt compilation and animation remain future
work as stated by the master vision.

### A10 exact implementation record

- `src/visual_engine/runtime/identity.py`: **1–28** — new low-level stable-digest owner that depends only on canonicalization.
- `src/visual_engine/runtime/versioning.py`: **1–184** — stable digest ownership removed from this module; public API remains compatible.
- `src/visual_engine/runtime/dependencies.py`: **1–142** — relation identity now consumes the lower-level digest primitive.
- `src/visual_engine/entities/face.py`: **1–n** — internal component imports routed to canonical common ownership.
- `src/visual_engine/persistence/postgres.py`: **1–n** — internal component imports routed to canonical common ownership.
- `src/visual_engine/persistence/serialization.py`: **1–n** — internal component/geometry/visual imports routed to canonical common ownership.
- `src/visual_engine/runtime/__init__.py`: **1–n** — stable digest exported through the lower-level owner while preserving the runtime API.
- `src/visual_engine/runtime/contract.py`: **1–n** — canonical common component/geometry/visual imports.
- `src/visual_engine/runtime/geometry_cache.py`: **1–n** — canonical common component/geometry imports.
- `src/visual_engine/runtime/geometry_fingerprint.py`: **1–n** — canonical common component/geometry imports.
- `src/visual_engine/runtime/graph.py`: **1–n** — canonical common component/relation imports.
- `src/visual_engine/runtime/spatial_relationships.py`: **1–n** — canonical common relation import.
- `src/visual_engine/runtime/state_policy.py`: **1–n** — canonical common component import.
- `src/visual_engine/runtime/versioning.py`: **1–n** — canonical common component import.
- `tests/unit/test_v13_a10_full_audit.py`: **1–110** — independent structural assertions.
- `tools/verify_a10_full_audit.py`: **1–240** — fail-closed second-audit verifier.
- `docs/governance/roadmap/ROADMAP__part_01.md`: this checkpoint section and current execution status.
- `docs/runtime/foundations/V1.3_AUDIT_AND_STATUS__part_01.md` (split document; see adjacent parts): A10 factual audit record.
- `docs/runtime/foundations/V1.3_IMPLEMENTATION_LOG__part_01.md` (split document; see adjacent parts): A10 chronological implementation record.
- `docs/governance/decisions/DECISIONS__part_01.md`: D-057.
- `docs/governance/architecture/ENGINE_VISION__part_01.md`: structural-hardening frontier updated to A10 closure.
- `docs/governance/architecture/ARCHITECTURE_CONTRACT__part_01.md`: A10 ownership/import-topology clarification.

## V1.4 — Eye Deepening Program — 2026-09-16

The V1.3 structural baseline is closed by A10. The next execution layer remains the eye, but the work is now decomposed
into atomic/subatomic units rather than broad feature labels.

**Canonical planning sources:**
- `docs/components/eyes/blueprint/V1.4_EYE_ATOMIC_BLUEPRINT__part_01.md`
- `docs/components/eyes/blueprint/index.json`
- `docs/components/eyes/blueprint/V1.4_EYE_EXECUTION_PROTOCOL.md`

The blueprint currently contains **284 atoms across 17 streams**. It records which atomic capabilities already have
implementation evidence and which remain partial/sketch. It does not promote parent workstreams to complete status.

### Execution discipline

Every atom must pass: **DEVELOP → TEST → ARTIFACT → VISUALIZE → CORRECT → VALIDATE → ACCEPT**.
A visual artifact without reproducible inputs, a preset without measurable effect, or a passing nominal test without
boundary/interaction evidence cannot close an atom.

### Eye execution order

`GEN → MOR/LID → IRI/PUP/LAS/BRW/HIL → EXP/PAIR/OCC → COL/STY → CAM → VAR → PRM → RND`.

The objective is a valid parameter manifold: a clean canonical default plus controlled continuous/discrete variation,
with correlations and hard invariants preventing invalid combinations. The target is not unconstrained randomness.

### V1.4 functional progress — MOR canthus brick

The first functional V1.4 morphology brick is accepted at atomic scope: independent inner/outer canthus roundness and closed-contour self-intersection protection. The implementation is owned by `eyes/geometry/canthus.py` and `eyes/geometry/invariants.py`; no facade or renderer owns this logic. `MOR.continuity`, global `MOR.morph_orthogonality` and the remaining morphology atoms stay open until their own evidence cycles pass.

### V1.4 functional progress — MOR.continuity

`MOR.continuity` is now accepted at atomic scope. The contour is traversed as upper
lid → outer cubic canthus bridge → lower lid → inner cubic canthus bridge. Bridge
endpoint derivatives are matched to adjacent lid endpoint derivatives (C1 under the
explicit interpolation convention), and the complete closed contour is rechecked
after gaze-follow. The zero-opening state remains an explicit degenerate boundary.
Evidence: `docs/components/eyes/morphology/V1.4_MOR_CONTINUITY_CONTRACT.md`,
`artifacts/v14_mor_continuity/` and `tools/visual_qa_v14_mor_continuity.py`.

`MOR.morph_orthogonality` and `MOR.morph_variation` remain open and are not promoted
by this result.


### V1.4 MOR orthogonality checkpoint

- [x] executable semantic-channel contract for `MOR.morph_orthogonality`;
- [x] eliminate contour-bound internal iris/pupil contamination;
- [x] add medial epicanthic-fold geometry at the inner canthus;
- [x] add hierarchical ocular granular visibility contract;
- [x] establish artifact timing overlay for geometry/SVG/PNG rendering;
- [ ] prompt parser integration with visibility IR remains future work.


### V1.4 MOR formal envelope measurement layer — 2026-09-17

A narrow measurement brick was implemented before any new geometry mutation.
`morphology/envelope.py` defines an invariant local frame from semantic canthi and measures
projected envelope height/aspect ratio, paired-lid opening maximum/ratio/area/balance,
opening location, upper/lower apex positions and lid-depth balance. It supports the existing
MOR atoms `shape_family`, `aspect_ratio`, `opening`, `upper_curve`, `lower_curve`, `rotation`
and `resolution` without duplicating their geometry solvers.

Evidence includes 12 deterministic visual cases and a 576-case metric stress matrix across
9 shape families × 4 opening boundaries × 4 sampling resolutions × 4 rotations, with gaze,
curve, asymmetry, contour-wave/irregularity and independent canthus values held in the stress
configuration. The metric layer fails closed on malformed input and does not invent resolution
invariance where the existing sampled geometry does not provide it.
