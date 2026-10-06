<!-- Refactored from docs/governance/roadmap/ROADMAP__part_01.md; source lines 379-525; content preserved. -->
<!-- Part 4/16. Use the family index for navigation. -->
## V1.3.6 — Relation → Placement → Semantic Target Resolution — 2026-09-14

Implemented the missing connection between the runtime relation graph and the
V1.3.5 generic placement solver.

### What was implemented

- `runtime/spatial_relationships.py`;
- validated `Relation.metadata["placement"]` contract;
- deterministic compilation into `PlacementIntent`;
- explicit semantic `target_region_id` support;
- explicit target anchor ownership (`component` or `region`);
- graph-wide deterministic placement resolution;
- fail-closed unknown-key and missing-anchor handling.

### How it was implemented

The relation compiler does not inspect component categories. It validates a small,
closed placement vocabulary, copies only explicit values into `PlacementIntent`, and
then delegates all geometry math to the existing placement solver. If a semantic
region is named, its geometry becomes the target geometry while the declared anchor
scope determines where the reference point is obtained.

### Verification

- full pytest suite: PASS;
- compileall: PASS;
- no object-specific placement branches added.

### Remaining work

The next gate is not a new category-specific solver. It is the constraint layer
needed to make relations spatially meaningful beyond a single anchor/scale:
explicit alignment, attachment, clearance, containment, contact and penetration
constraints with deterministic validation/resolution. Placement results then need
to participate in dependency fingerprints/cache invalidation before the pipeline is
connected automatically to visibility.

## V1.3.7 checkpoint — Hard Spatial Placement Constraints

The relation-to-placement path now supports an explicit hard-constraint layer for
containment, minimum clearance and non-penetration. Constraints are evaluated on
actual placed geometry and are enforced by the normal relation-placement resolver.
No general numerical optimizer or silent fallback was introduced.

Next gates remain separate: attachment/contact manifolds, orientation/alignment
frames, directional constraints, collision response, placement dependency
fingerprints/invalidation, and automatic placement→visibility materialization.

### V1.3 — Placement → Visibility closed loop

The generic spatial loop is now executable from an existing `PlacementSolution` through materialized source geometry and source semantic regions into the overlap-safe visibility kernel and structured `AffectedRegionEvent` output.

Next audit targets are multi-source attribution, placement dependency/invalidation, attachment/alignment frames, and integration of visibility results with declarative consequence resolution. Color remains intentionally outside this branch until the spatial loop is stable.

## V1.3 — Multi-occluder causal visibility attribution

Implemented `runtime/visibility_attribution.py`.

The target region is partitioned into a deterministic planar arrangement and every
cell receives its ordered front-occluder stack. The runtime now distinguishes
pairwise geometric coverage, exclusive coverage, shared coverage, depth-dominant
coverage and counterfactual optical marginal loss.

This closes the causal-attribution gap without changing the semantics of the
existing `AffectedRegionEvent` contract. No object category is inspected.

### Gate passed

- disjoint occluders: PASS;
- overlapping occluders: PASS;
- depth reversal: PASS;
- transmissive layer: PASS;
- counterfactual marginal loss: PASS;
- input-order determinism: PASS;
- duplicate-ID fail-closed validation: PASS;
- behind-layer exclusion: PASS;
- attribution invariants: PASS;
- full pytest suite: PASS;
- compileall: PASS.

### Boundary after this checkpoint

The engine now has spatial attribution for multiple planar occluders. It still does
not perform physical 3D optics, semantic consequence mutation, attachment/contact
manifolds, or appearance/color resolution.

The next architectural decision should be made from measured dependency needs,
not from visual feature requests.

## V1.3 — Causal Attribution → Consequence Compilation — 2026-09-14

Implemented the declarative bridge from the validated multi-occluder attribution
layer to the existing consequence resolver contract.

### Implemented

- attribution-specific predicates on `ConsequenceRule`;
- explicit `attribution_enabled` opt-in to prevent cross-domain false positives;
- deterministic `resolve_attribution_consequences()`;
- propagation of measured attribution metrics into `ConsequenceRequest.payload`;
- stable source-event domain marker `causal_attribution`;
- public runtime export;
- regression tests for domain isolation and attribution-specific matching.

### Architectural boundary

```text
AffectedRegionEvent → resolve_consequences()

OccluderAttribution → resolve_attribution_consequences()
```

The two event domains remain semantically distinct. Attribution is never converted
into an ordinary visibility event merely to reuse an existing API.

### Verification

- full `pytest -q`: PASS — 258 tests;
- `python -m compileall -q src`: PASS;
- attribution-domain opt-in regression: PASS.

### Next gate

Before appearance/color work, the remaining consequence boundary must be audited for
request aggregation, conflict/precedence semantics, idempotence, provenance and
invalidation. No downstream state/geometry/appearance mutation is claimed by this
checkpoint.

## V1.3 — Consequence Request Aggregation, Conflict, Precedence & Idempotence — 2026-09-14

Implemented `runtime/consequence_aggregation.py` as the explicit boundary after
`ConsequenceRequest` compilation.

### Implemented

- exact semantic request fingerprinting and idempotent deduplication;
- explicit conflict groups rather than target-based guessing;
- `KEEP_ALL`, `DEDUPLICATE`, `HIGHEST_PRIORITY`, and fail-closed
  `REJECT_CONFLICT` policies;
- downstream precedence separated from `ConsequenceRule.priority`;
- causal provenance retained for accepted/rejected decisions;
- deterministic ordering and result digest;
- mixed-target rejection;
- regression tests for duplicate, independent, conflict, precedence,
  determinism and provenance behavior.
