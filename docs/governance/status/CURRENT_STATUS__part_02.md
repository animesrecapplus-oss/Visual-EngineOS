<!-- Refactored from docs/governance/status/CURRENT_STATUS__part_01.md; source lines 139-277; content preserved. -->
<!-- Part 2/4. Use the family index for navigation. -->
## V1.37 — COLOR consumer audit — 2026-09-25

Current checkpoint: `V1.37_COLOR_CONSUMER_AUDIT`.

The V1.36 graph was re-opened and the current 171 production Python files were compared with
the V1.36 corrected source fingerprint. No source file was added, removed or changed.
The single true downstream color-modifying consumer is `runtime/effects.py`, which delegates
to the already-certified `runtime/effect_color.py` operation `effect.color.srgb8-interpolation`.
It is pre-existing, not new. Consequently no runtime COLOR algorithm was added in V1.37.

Fresh V1.37 focused tests: 47 passed, 0 failed. A real runtime sample was generated and
visually inspected. No monolithic repository-wide PASS is claimed from this focused run.

Next checkpoint: V1.38 effect-color semantic closure audit.

## V1.38 — EFFECT COLOR semantic closure — 2026-09-25

Current checkpoint: `V1.38_EFFECT_COLOR_SEMANTIC_CLOSURE`.

The existing `effect_color` path was audited end-to-end. There are exactly two production
`apply_effect_color()` call sites and two `_apply_canonical_effect()` call sites, both in
`runtime/effects.py`; no second RGB operation was found inside `effect_color.py`.

V1.38 corrected cumulative multi-effect lineage and closed a fingerprint dependency hole that
could have allowed an external effect fingerprint to mask an actual color mutation. Fill and
contour now share the same ordered lineage and immutable effect dependency fingerprint.

No new color space or color transformation was introduced. `ENGINE_VERSION` remains `1.3.8`,
`SCHEMA_VERSION` remains `2`, and `RESOLUTION_VERSION` advances `18 → 19` because invalidation/
provenance semantics changed.

Final composite test evidence: **870 passed, 1 skipped, 0 failed** across 871 collected tests.
The existing PostgreSQL integration skip remains conditional on `VISUAL_ENGINE_POSTGRES_DSN`.
A monolithic run reached ~90% before timeout; no monolithic PASS is claimed.

Current artifacts: `artifacts/v138_effect_color_closure/`. Superseded V1.37 current artifacts
were removed from this checkpoint.

Next checkpoint: V1.39 full resolution-fingerprint/cache closure around effect dependencies.

## V1.39 — Resolution fingerprint / cache closure — 2026-09-26

Current checkpoint: `V1.39_RESOLUTION_FINGERPRINT_CACHE_CLOSURE`.

V1.39 traced `ResolutionContext.effects → context_fingerprint() → resolution_fingerprint() → cache_identity` and proved the direct, legacy-shadow, relation and consequence effect paths. No missing production dependency was found. One false-positive dependency was found and corrected: inactive `state_priority` no longer invalidates a target when there are no active context states.

An actual bounded `ResolutionCache` is now available as an optional cache on `resolve_component()` and `resolve_component_contract()`. It uses only `ResolutionFingerprint.cache_identity`, returns immutable resolved results, records real hits/misses and performs no color work itself.

Fresh V1.39 focused tests: **20 passed, 0 failed**. Composite execution: **891 collected / 890 passed / 1 skipped / 0 failed** across 104 test files. The existing PostgreSQL integration test remains the one conditional skip. A monolithic 900-second run reached 96% before timeout; no monolithic PASS is claimed.

`ENGINE_VERSION=1.3.8`, `SCHEMA_VERSION=2`, `RESOLUTION_VERSION=20`.

No new color space or color transformation was introduced. Current artifacts are under `artifacts/v139_resolution_cache_closure/`; V1.38 current generated artifacts were removed after evidence capture.

Next checkpoint: V1.40 cache lifecycle / cross-surface invalidation closure.

## V1.40 — ResolutionCache lifecycle / cross-surface invalidation — 2026-09-26

Current checkpoint: `V1.40_RESOLUTION_CACHE_LIFECYCLE`.

V1.40 audited every concrete `ResolutionCache(...)` construction and found **0 production instantiations**. The cache remains caller-owned and optional; current constructions are test-local or tool-local. No component-, scene-, or process-global cache was invented.

`resolve_component()` now checks `RuntimeGraph.is_current()` before calculating or looking up a cache identity. Stale graphs fail closed before `ResolutionCache.get()`. Rebuilt graphs reuse entries when the existing target `ResolutionFingerprint.cache_identity` is unchanged. Target-relevant relation/hierarchy mutations produce new identities; unrelated sibling mutations can remain isolated after rebuild.

Cross-surface probes confirmed: visual-only changes affect resolution but not geometry; relation topology can affect both; relation effect metadata affects resolution but not geometry; geometry input changes both because resolved output contains geometry.

Real LRU pressure was measured at 1 / 10 / 100 / 1,000 capacities. Concurrent resolver reads/writes preserved visual/provenance consistency and cache bounds. Statistics are already immutable snapshots; no reset API was added. No serialized cache envelope is needed today.

Focused V1.39 + V1.40 + RuntimeGraph regression tests: **43 passed, 0 failed**. Full repository validation is executed in deterministic batches; the V1.40 report records the final batch result before certification. `compileall` passes.

`ENGINE_VERSION=1.3.8`, `SCHEMA_VERSION=2`, `RESOLUTION_VERSION=20`. No new COLOR transformation was introduced.

Current generated evidence is under `artifacts/v140_resolution_cache_lifecycle/`; superseded current V1.39 generated artifacts are removed from the V1.40 checkpoint after evidence capture.

Next checkpoint: V1.41 concurrent same-key build / cache hand-off and real lifetime-pressure audit.

## V1.41 — ResolutionCache same-key single-flight — 2026-09-27

Current checkpoint: `V1.41_RESOLUTION_CACHE_SINGLEFLIGHT`.

V1.41 reproduced and closed the real concurrent same-key MISS race. Before the change,
2/4/8/16 simultaneous callers could build 2/4/8/16 independent `ResolvedComponent` objects.
After the change, the same forced race produces exactly one build and the same immutable
result for all callers; 32-worker evidence was also measured.

`ResolutionCache.get_or_build()` now owns same-key build coalescing through a per-fingerprint
`Event`. The cache lock is not held while resolver work executes, so unrelated keys remain
parallel. Builder exceptions propagate to current waiters and failed keys can be retried.
A generation counter makes `clear()` a true lifecycle boundary: pre-clear active builds cannot
repopulate the cleared cache, and new callers cannot join the old generation.

The cache remains caller-owned. AST evidence still finds **0 production `ResolutionCache(...)`
instantiations**; no scene/frame/process singleton was introduced. A caller-owned cache hand-off
across two rebuilt graph/frame-style boundaries was tested and reuses the same immutable result
when the fingerprint is unchanged.

Real memory measurements report approximately 5,773 bytes for one fixture `ResolvedComponent`
and approximately 6,222 / 35,435 / 331,201 / 3,277,941 bytes for cache-entry graphs containing
1 / 10 / 100 / 1,000 distinct results. These are Python engineering measurements, not a production
allocator certification.

Final repository collection: **918 tests across 105 test files**. Deterministic batch execution:
**917 passed / 1 skipped / 0 failed**; the skip is the existing PostgreSQL integration test
requiring `VISUAL_ENGINE_POSTGRES_DSN`. The final V1.41 frame-handoff test was then run independently
and passed. `compileall` passed.

`ENGINE_VERSION=1.3.8`, `SCHEMA_VERSION=2`, `RESOLUTION_VERSION=20`.

No COLOR runtime file changed and no new color transformation was introduced. Current generated
evidence is under `artifacts/v141_resolution_cache_singleflight/`; V1.40 current generated artifacts
are removed after evidence capture. V1.40 reports/contracts remain in `docs/` for history.

Next checkpoint: **V1.42 — real production cache lifetime / frame-scene ownership audit**, only if a
real production consumer can be identified. No global cache manager should be invented in its absence.

## V1.42 — ResolutionCache production lifetime / frame-scene ownership — 2026-09-27

V1.42 searched the production source graph for a real owner of `ResolutionCache` and found none: 0 production cache instantiations and 0 downstream production resolver call sites. The renderer consumes eye geometry/appearance directly; scene composition and shot data are not connected to generic component resolution. `ResolutionCache` therefore remains explicitly caller-owned; no global/process/scene/frame manager is introduced.

A diagnostic, explicitly non-production frame loop using real `Component` + `RuntimeGraph` + `resolve_component()` + `ResolutionCache` rebuilt a 32-component graph for 60 boundaries: 32 first-boundary misses, then 1,888 hits and 0 misses. Fully compiled production graphs were measured at 1 / 10 / 100 / 1,000 components; memory and rebuild churn were measured with `tracemalloc` and local timing. Exact-identical independent graphs demonstrated cross-graph reuse through a shared cache; equal-budget distinct graphs showed no hidden advantage for partitioning in the tested alternating workload.

Teardown verified that cached `ResolvedComponent` results do not retain the authoring `Component` tree or `RuntimeGraph`. No fingerprint persistence consumer exists, so no persistence envelope was added. `ResolutionFingerprint.cache_identity` remains the sole cache identity. V1.39/V1.40/V1.41 cache/concurrency and COLOR regression surfaces passed. Only `src/visual_engine/runtime/resolution_cache.py` changed in production, and only its caller-owned class documentation was extended. COLOR runtime files remain unchanged; `RESOLUTION_VERSION=20` remains unchanged.

**V1.42 status:** `ENGINEERING PASS / ZERO PRODUCTION CACHE OWNER / CALLER-OWNED LIFETIME EXPLICIT / FRAME-STYLE REUSE MEASURED / CARDINALITY + MEMORY MEASURED / REBUILD CHURN MEASURED / SHARED VS PARTITIONED MEASURED / TEARDOWN PASS / NO PERSISTENCE / NO NEW COLOR TRANSFORMATION`.

Evidence: `docs/runtime/cache/V1.42_RESOLUTION_CACHE_LIFETIME_CONTRACT__part_01.md` (split document; see adjacent parts), `docs/runtime/cache/V1.42_IMPLEMENTATION_REPORT_2026-09-27__part_01.md` (split document; see adjacent parts), `tools/audit_v142_resolution_cache_lifetime.py`, `tools/verify_v142_resolution_cache_lifetime.py`, `tools/benchmark_v142_resolution_cache_lifetime.py`, `tools/visual_qa_v142_resolution_cache_lifetime.py`, `artifacts/v142_resolution_cache_lifetime/`.

## V1.43 — 2026-09-28 — first production consumer audit

V1.43 searched all 172 production Python files for the first real downstream caller of `resolve_component()` / `resolve_component_contract()` and for a production `ResolutionCache` owner. Both counts remain zero. The renderer, scene/frame/shot composition and PostgreSQL graph compilation do not form a generic-resolution production path.

Therefore `ResolutionCache` remains explicitly caller-owned. No global/scene/frame/request owner, partitioning API, byte budget or persistence envelope was added. Diagnostic measurements using real production objects demonstrate frame-style cache reuse, scene-adjacent placement cardinality, retained Python memory, rebuild churn and exact-identity shared-cache reuse, but they are not claimed as production workload measurements.

Current repository evidence: 923 collected tests across 106 files, 922 passed, 1 PostgreSQL integration skip requiring `VISUAL_ENGINE_POSTGRES_DSN`, 0 failed. Production `src/` is unchanged from V1.42. COLOR runtime files remain unchanged and `RESOLUTION_VERSION=20` remains current.

Historical V1.43 current-artifact directory was removed from the V1.44 release tree; its evidence remains in the V1.43 report/checkpoint.

**V1.43 status:** `ENGINEERING PASS / ZERO PRODUCTION RESOLVER CONSUMERS / ZERO PRODUCTION CACHE OWNERS / CALLER-OWNED / NO INVENTED ORCHESTRATION / TEARDOWN VERIFIED / SHARED VS PARTITIONED MEASURED / NO PERSISTENCE / NO MEMORY BUDGET / COLOR UNCHANGED`.
