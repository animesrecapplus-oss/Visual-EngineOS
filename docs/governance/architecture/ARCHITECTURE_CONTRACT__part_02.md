<!-- Refactored from docs/governance/architecture/ARCHITECTURE_CONTRACT__part_01.md; source lines 143-256; content preserved. -->
<!-- Part 2/2. Use the family index for navigation. -->
## A0 ocular correctness clarifications — 2026-09-15

The default ocular contract now includes three verified invariants:

1. Extreme gaze may place the iris/pupil assembly center at the resolved eye aperture;
   the aperture clips the assembly footprint.
2. Closed/covered eyes emit no default lash geometry.
3. Brow vertical placement is bounded by explicit eye-gap constraints regardless of
   expression intent.

Projected shadows from external occluders remain a separate appearance/lighting domain;
visibility coverage must not be treated as a shadow implementation.

## A0 structural closure clarifications — 2026-09-15

### RuntimeGraph lifecycle
`RuntimeGraph` is a compiled index over an authoring `Component` tree, not a second mutable
source of truth. Its index containers are immutable. Hierarchy/relation topology changes after
compilation invalidate the graph and must be followed by `graph.rebuild()`. Queries fail fast
on stale topology instead of silently returning stale indexes. Local visual/geometry mutation
without topology change remains owned by resolution/cache fingerprints.

### PostgreSQL lifecycle
PostgreSQL remains a cold-path source of truth. Migration execution is explicit, ordered,
transactional and recorded in `schema_versions`. Missing earlier migrations after a later
migration, or unknown migration identifiers, are hard errors. The renderer must never issue
per-component/per-pixel database queries.

### Eyebrow / closed-eye reference frame
Eyebrow placement must not derive its anatomical reference scale from state-dependent visible
aperture height. Closed/covered eyes have zero visible aperture by design; superior facial
features therefore use a stable full-opening eye/upper-lid reference. The brow gap is a hard
constraint, not an expression suggestion.

## A0 re-audit 2 clarifications — 2026-09-15

### PostgreSQL migration integrity

A migration is considered applied only after its exact checked-in SQL has executed successfully in
the same transaction as its `schema_versions` ledger insertion. Each ledger row carries a SHA-256
checksum of the migration SQL. Unknown versions, gaps, checksum drift and checksum-less legacy
history are hard errors. A transaction-scoped advisory lock serializes concurrent migration
runners for the same database.

A normal application test may skip when no PostgreSQL DSN exists, but the strict
`tools/verify_live_postgres.py` gate must fail closed when no DSN/server is available. Absence of a
server is never a successful integration result.

### RuntimeGraph lifecycle integrity

RuntimeGraph compilation must reject cycles, repeated component-object references and inconsistent
child/parent links before constructing indexes. The graph is a compiled topology view; authoring
topology mutation invalidates it and requires `rebuild()`. Content mutation is intentionally a
separate cache/resolution concern.

### Ocular superior-feature invariant

Eyebrow placement is anchored to a stable full-opening superior ocular reference. State-dependent
visible aperture height must not become the coordinate system for superior facial features. The
minimum/maximum brow-eye gap remains a hard constraint after expression/gaze coupling.


## A3 — Geometry fingerprint identity boundary

The geometry cache uses a versioned, deterministic fingerprint contract. The local geometry
identity includes kind, parameters, anchors, constraints, profiles, state, authored geometry
and explicit generator cache inputs. It excludes component ID (owned by the cache key), visual
contracts, visual overrides, appearance-only data and transforms. Any geometry-relevant value
derived from another domain must be projected by the generator into explicit cache inputs.
Unordered containers, non-string mapping keys, non-finite floats, cyclic values and arbitrary
objects are rejected at the fingerprint boundary. The fingerprint contract version is part of
the hashed payload and therefore creates an explicit invalidation boundary when semantics change.


## A4 — Master documentation synchronization — 2026-09-16

The following documents form one synchronized status surface:

- `ENGINE_VISION.md` — permanent architectural intent;
- `ARCHITECTURE_CONTRACT.md` — concise normative rules;
- `ARCHITECTURE_PRINCIPLES.md` — non-negotiable principles;
- `ROADMAP.md` — current execution order and historical checkpoints;
- `V1.3_AUDIT_AND_STATUS.md` — factual implementation/test ledger;
- `V1.3_IMPLEMENTATION_LOG.md` — chronological implementation record;
- `DECISIONS.md` — uniquely identified architectural decisions.

Historical sections are retained for provenance but cannot override the current status surface.
A4 also closes duplicate decision identifiers so a decision ID has exactly one owner.

## A7 generic PostgreSQL persistence vertical slice — 2026-09-16

The generic persistence boundary now has a complete offline-verifiable authoring-graph path
beyond migration lifecycle. `PostgresEntityRepository.save_component_tree()` compiles and validates
the `RuntimeGraph` before opening the database, then writes the entity record, immutable entity
version and relational component projection in one transaction. `load_component_tree()` hydrates
one entity with bounded relation-family queries and recompiles the loaded graph before returning it.

Stable/queryable facts remain relational (`components`, `relations`, `constraints`, `profiles`,
`appearance_layers`, `component_states`). Extensible transform/visual/geometry contracts are kept
in component `metadata` JSONB so adding a new renderer-neutral field does not require a migration
for every contract extension. Sibling order is explicitly persisted because SQL rows are unordered.

JSONB encoding is deterministic and rejects NaN/infinity and unsupported Python objects. Entity root
kind and integer seed are validated before SQL. The renderer remains prohibited from database access
in hot/per-pixel loops. Live PostgreSQL execution remains a separate environment gate and is not
claimed by A7 in an environment without a configured server.

## A10 — Canonical ownership and dependency-topology invariant

The canonical implementation of shared component contracts lives under `components.common`. The historical
`visual_engine.model` package is compatibility-only and must not be imported by internal runtime/persistence/domain
modules. New low-level identity primitives must not depend upward on graph, cache or resolution layers. Top-level
internal imports must remain acyclic; compatibility bridges that require deferred imports must be explicitly marked
as such and must not become a second implementation owner.
