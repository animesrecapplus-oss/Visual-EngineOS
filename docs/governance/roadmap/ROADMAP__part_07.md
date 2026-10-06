<!-- Refactored from docs/governance/roadmap/ROADMAP__part_01.md; source lines 792-929; content preserved. -->
<!-- Part 7/16. Use the family index for navigation. -->
### Exact affected lines

Line numbers are recorded after implementation and verification; they are checkpoint
coordinates, not immutable API coordinates after future edits.

- `src/visual_engine/runtime/version_policy.py`: **1–34** — new canonical policy.
- `src/visual_engine/runtime/versioning.py`: **36–45** — `VersionStamp` defaults consume policy constants.
- `src/visual_engine/runtime/__init__.py`: policy export addition.
- `src/visual_engine/__init__.py`: package version derives from `ENGINE_VERSION`.
- `src/visual_engine/persistence/schema.py`: independent engine/schema serialization defaults.
- `tools/verify_a6_version_policy.py`: cross-surface drift verifier.
- `tests/unit/test_v13_a6_version_policy.py`: policy, packaging, serialization and historical-override tests.
- `tests/unit/test_persistence.py`: engine/schema expectation corrected.
- `docs/runtime/foundations/V1.3_VERSION_INVALIDATION_CONTRACT.md`: A6 canonical-policy section.
- `docs/governance/roadmap/ROADMAP__part_01.md`: current authoritative status, implementation boundary, execution order and this checkpoint.
- `docs/runtime/foundations/V1.3_AUDIT_AND_STATUS__part_01.md` (split document; see adjacent parts): current A6 status and checkpoint history.
- `docs/runtime/foundations/V1.3_IMPLEMENTATION_LOG__part_01.md` (split document; see adjacent parts): A6 chronological implementation record.
- `docs/governance/decisions/DECISIONS__part_01.md`: D-053.

## V1.3 — A7 generic PostgreSQL persistence vertical slice — 2026-09-16

**Status: implemented and offline-verified; live PostgreSQL remains unverified.**

A7 was audited against the A6 checkpoint before implementation. Migration lifecycle and the simple
`save_entity/load_entity` path already existed, so they were retained. The missing tranche was the
generic authoring-graph vertical slice: parameters, anchors, hierarchy, relations, constraints,
profiles, appearance layers, state layers, transform/visual/geometry contracts, immutable entity
versions, deterministic hydration, and fail-closed validation.

- [x] generic component-tree persistence API
- [x] immutable `entity_versions` snapshot allocation under entity-row lock
- [x] relational projection for components/relations/constraints/profiles/appearance/state
- [x] JSONB metadata for extensible transform/visual/geometry contracts
- [x] deterministic sibling ordering persistence
- [x] bounded load queries with no per-component N+1 database access
- [x] topology validation before write and after load
- [x] root-kind and seed validation before SQL
- [x] deterministic JSONB encoding with non-finite/unsupported-value rejection
- [x] serialization round-trip tests
- [x] strict offline A7 verifier
- [ ] live PostgreSQL server round-trip — requires an explicit PostgreSQL DSN/server

A7 does **not** claim production database performance, distributed deployment behavior, backup/
restore correctness, connection-pool tuning, migration rollback, or live PostgreSQL compatibility.
Those require a real database environment and remain separate evidence gates.

### A7 exact implementation record

- `src/visual_engine/persistence/serialization.py`: **1–178** — new generic component contract serializer/deserializer; transform/visual/geometry metadata and explicit child-order provenance.
- `src/visual_engine/persistence/postgres.py`: **1–292** — generic graph save/load transaction, immutable entity-version allocation, relational projections, bounded hydration and fail-closed validation.
- `src/visual_engine/persistence/__init__.py`: **1–11** — public serializer exports.
- `tools/verify_a7_persistence.py`: **1–102** — strict offline verifier.
- `tests/unit/test_v13_a7_persistence_vertical_slice.py`: **1–109** — serializer, JSONB, topology and bounded-query regression tests.
- `docs/governance/architecture/ARCHITECTURE_CONTRACT__part_01.md`: A7 normative persistence boundary appended at final checkpoint.
- `docs/governance/roadmap/ROADMAP__part_01.md`: current A7 status and checkpoint history.
- `docs/runtime/foundations/V1.3_AUDIT_AND_STATUS__part_01.md` (split document; see adjacent parts): A7 audit/implementation/verification record.
- `docs/runtime/foundations/V1.3_IMPLEMENTATION_LOG__part_01.md` (split document; see adjacent parts): chronological A7 record.
- `docs/governance/decisions/DECISIONS__part_01.md`: D-054.


## V1.3 — A8 generic end-to-end cross-layer verification — 2026-09-16

**Status: implemented and verified offline.**

Pre-implementation audit found that A8 was **not** already closed. Existing vertical-slice tests were
either eye-specific or PostgreSQL-specific; no single deterministic gate traversed the generic authoring
graph through RuntimeGraph, appearance resolution, geometry generation/cache, spatial placement,
renderer-neutral evidence, and persistence serialization. A8 therefore adds one verification harness
instead of duplicating existing domain implementations.

Implemented:
- deterministic three-node `HumanFace -> Eye/Eye` fixture with bilateral relation metadata;
- RuntimeGraph compilation and stale-topology rejection check;
- generic visual resolution with versioned fingerprint;
- BASE appearance-domain resolution;
- `face.human_with_eyes` dependency-driven geometry generation through `CachedGeometryGenerator`;
- cache miss -> cache hit verification;
- local -> camera geometry transformation through the existing transform contract;
- fail-closed renderer-neutral evidence adapter for emitted path/ellipse primitives;
- SVG XML well-formedness and finite-number checks;
- deterministic component serialization evidence;
- explicit PostgreSQL status: live SQL remains unverified unless a DSN is supplied;
- clean-run reproducibility covered by the A8 regression tests.

Files created:
- `tools/verify_a8_e2e.py`
- `tests/unit/test_v13_a8_e2e.py`
- `artifacts/history/v1.3/a8_e2e/REPORT.json`
- `artifacts/history/v1.3/a8_e2e/a8_face_camera.svg`
- `artifacts/history/v1.3/a8_e2e/a8_serialized_components.json`

No production renderer, PostgreSQL driver, or second persistence model was introduced. The evidence
renderer is deliberately local to the A8 verification boundary and fails closed on unsupported primitive
or mask types. A8 proves cross-layer wiring and determinism; it does **not** prove artistic quality,
physical optics, production rendering fidelity, or live PostgreSQL execution. A9 remains responsible
for the broader adversarial/property-style suite.


## V1.3 — A9 adversarial/property hardening + responsibility refactor — 2026-09-16

**Status: implemented and verified offline.**

### Pre-implementation audit

A9 was not treated as a blank test feature. Existing tests already covered several individual invariants
(cycles/stale graphs, geometry fingerprints, transforms, visibility ordering and cache behavior), so those
were retained. The audit identified two concrete gaps: deterministic identity canonicalization could silently
coerce non-string mapping keys and recurse indefinitely on cyclic values, and the largest ocular/SVG/cache
modules mixed public compatibility facades with implementation responsibilities.

### Implementation

- Added a fail-closed canonicalization primitive with cycle detection, finite-number checks and strict string
  mapping-key policy.
- Hardened geometry metadata normalization against cycles and key coercion.
- Added cache-key field validation and dependency-ID validation before LRU mutation.
- Split the ocular `core.py` into a compatibility facade, domain definitions, and geometry construction.
- Split SVG implementation into geometric primitives, ocular effects, contours/state, with a small public facade.
- Split geometry-cache identity/fingerprint logic from cache concurrency/eviction policy while preserving the
  historical import surface.
- Added deterministic adversarial/property-style tests for canonicalization, cycles, permutations, mutation,
  cache invalidation, concurrency, hostile metadata and degenerate transforms.
- Added a strict A9 verifier with structural line-budget guardrails for the refactored facades.
- Added `.` to pytest's configured Python path so repository-local verification modules are importable under
  both `pytest` and `python -m pytest`.

### Explicit nonclaims

A9 is not a claim of exhaustive fuzzing, formal verification, live PostgreSQL validation, production renderer
performance, or proof that every future component type satisfies every possible invariant. The refactor is
responsibility-oriented rather than a cosmetic line-count exercise; the remaining 300–400-line runtime modules
were not fragmented without a demonstrated independent responsibility boundary.

### A9 exact implementation record

Final line coordinates are recorded in `docs/runtime/foundations/V1.3_IMPLEMENTATION_LOG__part_01.md` (split document; see adjacent parts) after all source/test edits.
