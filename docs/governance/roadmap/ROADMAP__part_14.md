<!-- Refactored from docs/governance/roadmap/ROADMAP__part_01.md; source lines 1740-1882; content preserved. -->
<!-- Part 14/16. Use the family index for navigation. -->
## V1.37 completion — COLOR consumer audit — 2026-09-25

- [x] Re-open V1.36 consumer graph.
- [x] Compare current runtime source against V1.36 immutable fingerprint.
- [x] Identify one actual color-modifying consumer.
- [x] Separate representation, measurement, palette, rendering and transformation.
- [x] Confirm the actual transformation is pre-existing and already closed.
- [x] Re-audit transformation contract across alpha/gamut/provenance/lineage/fingerprint/invalidation/cache/determinism/performance/visual criteria.
- [x] Add adversarial runtime tests.
- [x] Generate and visually inspect runtime-backed samples.
- [x] Do not add a duplicate runtime transformation.
- [x] Package V1.37 checkpoint without obsolete temporary artifacts.

## V1.38 completion — EFFECT COLOR semantic closure — 2026-09-25

- [x] enumerate every production `apply_effect_color()` caller
- [x] enumerate every production `_apply_canonical_effect()` caller
- [x] prove one alpha authority: `VisualEffect.alpha`
- [x] prove `effect.color.alpha` is not implicitly consumed by production RGB logic
- [x] verify fill and contour carry identical cumulative effect lineage
- [x] verify shadow→shadow, tint→tint, shadow→tint and tint→shadow sequences
- [x] verify canonical effect priority/order and equal-priority tie-breaking
- [x] verify duplicate effect IDs fail closed
- [x] verify fingerprint invalidation for color, alpha, order, source, effect ID and operation version
- [x] close external-effect-fingerprint masking of actual effect-color changes
- [x] measure real 0/1/2/multiple-effect resolver cost
- [x] generate and visually inspect a real multi-effect board covering dark/mid/high/close/complementary/alpha cases
- [x] audit `effect_color.py` for a hidden second color operation
- [x] optimize repeated effect fingerprinting and base RGBA8 decoding without changing the RGB law
- [x] bump resolution identity 18 → 19 because provenance/invalidation semantics changed
- [x] remove superseded V1.37 current artifact directory after evidence capture
- [x] package V1.38 with deterministic audit, gate, benchmark and visual evidence
- [ ] introduce another color transformation only if a distinct real production consumer is proven

**V1.38 status:** `ENGINEERING PASS / EFFECT COLOR SEMANTIC CLOSURE PASS / NO SECOND COLOR TRANSFORMATION / ALPHA CLOSED / LINEAGE CLOSED / FINGERPRINT CLOSED / VISUAL EVIDENCE INSPECTED`.

Evidence: `docs/domains/color/V1.38_EFFECT_COLOR_SEMANTIC_CLOSURE_CONTRACT__part_01.md` (split document; see adjacent parts), `docs/domains/color/V1.38_IMPLEMENTATION_REPORT_2026-09-25__part_01.md` (split document; see adjacent parts), `tools/audit_v138_effect_color_closure.py`, `tools/verify_v138_effect_color_closure.py`, `tools/benchmark_v138_effect_color.py`, `tools/visual_qa_v138_effect_color_closure.py`, `artifacts/v138_effect_color_closure/`.

## V1.39 completion — Resolution fingerprint / cache closure — 2026-09-26

- [x] trace `ResolutionContext.effects`
- [x] trace `context_fingerprint()`
- [x] trace `resolution_fingerprint()`
- [x] verify color/alpha/source/effect ID/priority-order/version invalidation
- [x] verify direct context, legacy shadow, relation and consequence effect paths
- [x] compare local `effect_color` fingerprint with global resolution fingerprint
- [x] audit duplicate and missing dependencies
- [x] verify canonicalized input order equivalence
- [x] test duplicate IDs through mixed direct/relation paths
- [x] implement an actual bounded resolution cache keyed only by `ResolutionFingerprint.cache_identity`
- [x] measure real cache misses/hits for 0/1/2/4/8 effects
- [x] generate and inspect before/after-cache visual runtime board
- [x] verify cache preserves color and provenance
- [x] audit deterministic fingerprint serialization
- [x] find and correct inactive-state-priority false invalidation
- [x] advance resolution identity 19 → 20
- [x] remove superseded V1.38 current artifact directory
- [x] package deterministic V1.39 audit/cache/performance/visual evidence
- [ ] introduce another color transformation only if a distinct real production consumer is proven

**V1.39 status:** `ENGINEERING PASS / RESOLUTION FINGERPRINT CACHE CLOSURE PASS / FALSE INVALIDATION CORRECTED / CACHE HIT-MISS VERIFIED / VISUAL EQUIVALENCE INSPECTED / NO NEW COLOR TRANSFORMATION`.

Evidence: `docs/runtime/cache/V1.39_RESOLUTION_FINGERPRINT_CACHE_CLOSURE_CONTRACT__part_01.md` (split document; see adjacent parts), `docs/runtime/cache/V1.39_IMPLEMENTATION_REPORT_2026-09-26__part_01.md` (split document; see adjacent parts), `tools/audit_v139_resolution_cache_closure.py`, `tools/verify_v139_resolution_cache_closure.py`, `tools/benchmark_v139_resolution_cache.py`, `tools/visual_qa_v139_resolution_cache.py`, `artifacts/v139_resolution_cache_closure/`.

### V1.40 completion — ResolutionCache lifecycle / cross-surface invalidation — 2026-09-26

- [x] enumerate every concrete `ResolutionCache(...)` construction with AST evidence
- [x] prove zero production component/scene/process cache construction
- [x] verify caller-owned cache lifetime and reuse across repeated resolutions
- [x] enforce stale `RuntimeGraph` rejection before cache lookup
- [x] test unchanged `RuntimeGraph.rebuild()` cache reuse
- [x] test unrelated sibling topology isolation after rebuild
- [x] test relation add/remove with miss and restored-identity hit
- [x] test hierarchy reparenting with a visibly changed inherited result
- [x] compare resolution and geometry dependency ownership
- [x] measure LRU pressure at 1/10/100/1,000 capacities
- [x] verify LRU eviction remains bounded and deterministic
- [x] test concurrent reads/writes and bounded cache state
- [x] verify statistics are immutable snapshots; defer reset API
- [x] determine that serialized fingerprint persistence is not currently required
- [x] generate and visually inspect the larger hierarchy/relation/consequence/context board
- [x] keep the COLOR boundary unchanged
- [x] remove superseded current V1.39 generated artifacts after evidence capture

**V1.40 status:** `ENGINEERING PASS / CACHE LIFETIME AUDITED / STALE GRAPH GUARD CLOSED / GRAPH REBUILD REUSE VERIFIED / LRU PRESSURE VERIFIED / CROSS-SURFACE DEPENDENCIES VERIFIED / CONCURRENCY VERIFIED / VISUAL EVIDENCE INSPECTED / NO NEW COLOR TRANSFORMATION`.

Evidence: `docs/runtime/cache/V1.40_RESOLUTION_CACHE_LIFECYCLE_CONTRACT__part_01.md` (split document; see adjacent parts), `docs/runtime/cache/V1.40_IMPLEMENTATION_REPORT_2026-09-26__part_01.md` (split document; see adjacent parts), `tools/audit_v140_resolution_cache_lifecycle.py`, `tools/benchmark_v140_resolution_cache_lifecycle.py`, `tools/visual_qa_v140_resolution_cache_lifecycle.py`, `artifacts/v140_resolution_cache_lifecycle/`.

### V1.41 next micro-scope

1. measure duplicate builds under concurrent same-key misses;
2. decide whether single-flight build coalescing is justified by measured contention;
3. audit explicit cache hand-off across frame/scene lifetimes without introducing global ownership;
4. measure memory pressure using real `ResolvedComponent` size rather than entry count alone;
5. test immutable result sharing across frame boundaries;
6. audit whether an explicit `get_or_build_for_graph()` API would improve lifetime safety;
7. define telemetry requirements only if a real consumer exists;
8. repeat cross-surface invalidation tests after any lifecycle change;
9. keep the COLOR boundary unchanged unless a distinct real production consumer is independently proven.

### V1.41 completion — ResolutionCache same-key single-flight / lifecycle race closure — 2026-09-27

- [x] reproduce the V1.40 same-key concurrent MISS race before changing production code
- [x] quantify redundant builds at 2 / 4 / 8 / 16 callers
- [x] make `ResolutionCache.get_or_build()` the production build boundary
- [x] coalesce only identical `ResolutionFingerprint.cache_identity` values
- [x] preserve unrelated-key parallelism
- [x] share the exact immutable `ResolvedComponent` object with waiters
- [x] propagate the owner builder exception to current waiters
- [x] allow failed keys to be retried by later callers
- [x] audit and close the `clear()` active-build repopulation race with a generation boundary
- [x] release completed in-flight state so it does not become a second unbounded cache
- [x] re-run cross-surface resolution/geometry dependency partition
- [x] verify zero production cache instantiations remain
- [x] test caller-owned cache hand-off across rebuilt frame-style boundaries
- [x] measure real `ResolvedComponent` retained object size at 1 / 10 / 100 / 1,000 results
- [x] measure forced same-key concurrency at 2 / 4 / 8 / 16 / 32 callers
- [x] generate and visually inspect the real single-flight runtime board
- [x] preserve immutable statistics snapshots; add no telemetry without a consumer
- [x] preserve `ResolutionFingerprint.cache_identity` as the sole cache identity
- [x] keep the COLOR boundary unchanged
- [x] remove superseded current V1.40 generated artifacts after evidence capture

**V1.41 status:** `ENGINEERING PASS / SAME-KEY SINGLE-FLIGHT PASS / EXCEPTION PROPAGATION CLOSED / CLEAR GENERATION RACE CLOSED / DISTINCT-KEY PARALLELISM VERIFIED / MEMORY EVIDENCE CAPTURED / VISUAL EVIDENCE INSPECTED / NO NEW COLOR TRANSFORMATION`.

Evidence: `docs/runtime/cache/V1.41_RESOLUTION_CACHE_SINGLEFLIGHT_CONTRACT__part_01.md` (split document; see adjacent parts), `docs/runtime/cache/V1.41_IMPLEMENTATION_REPORT_2026-09-27__part_01.md` (split document; see adjacent parts), `tools/audit_v141_resolution_cache_singleflight.py`, `tools/benchmark_v141_resolution_cache_singleflight.py`, `tools/visual_qa_v141_resolution_cache_singleflight.py`, `artifacts/v141_resolution_cache_singleflight/`.

### V1.42 next micro-scope

1. search for the first real production caller that could own a `ResolutionCache`;
2. if none exists, keep the cache caller-owned and do not invent a renderer/global owner;
3. inspect renderer/frame/scene orchestration for a natural cache hand-off point;
4. if a real consumer exists, test lifetime across actual frame boundaries rather than simulated ones;
5. measure capacity against real scene/component cardinality;
6. measure retained memory with the real production object graph/allocator if a consumer exists;
7. compare cache reuse against graph rebuild frequency and dependency churn;
8. determine whether scene/frame partitioning would reduce LRU pollution;
9. test teardown so discarded scenes cannot retain live component graphs through cached results;
10. revisit serialized fingerprint envelopes only if a real persistence/restart requirement appears;
11. keep `ResolutionFingerprint.cache_identity` as the sole dependency identity;
12. repeat cross-surface invalidation and concurrent tests after any lifetime change;
13. preserve the COLOR boundary strictly.
