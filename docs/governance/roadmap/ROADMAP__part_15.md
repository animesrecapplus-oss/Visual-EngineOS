<!-- Refactored from docs/governance/roadmap/ROADMAP__part_01.md; source lines 1883-2002; content preserved. -->
<!-- Part 15/16. Use the family index for navigation. -->
### V1.42 completion — ResolutionCache production lifetime / frame-scene ownership — 2026-09-27

- [x] search the production source graph for the first real `ResolutionCache` owner
- [x] prove zero production cache instantiations
- [x] prove zero downstream production generic resolver consumers
- [x] audit renderer/frame/scene/shot orchestration instead of assuming it exists
- [x] keep the cache explicitly caller-owned when no owner exists
- [x] measure frame-style lifetime using real production runtime classes
- [x] measure fully compiled graph cardinality at 1 / 10 / 100 / 1,000 components
- [x] measure production-object memory with `tracemalloc`
- [x] measure RuntimeGraph rebuild churn
- [x] compare shared and partitioned cache behavior
- [x] verify exact-identity reuse across independent graph objects
- [x] verify teardown does not retain the authoring scene through cache results
- [x] verify no real fingerprint persistence consumer exists
- [x] preserve `ResolutionFingerprint.cache_identity` as the sole semantic cache identity
- [x] rerun cross-surface and concurrency regression tests
- [x] generate and visually inspect a real resolver lifetime/ownership board
- [x] preserve the COLOR boundary
- [x] remove superseded current V1.41 generated artifacts after evidence capture

**V1.42 status:** `ENGINEERING PASS / ZERO PRODUCTION CACHE OWNER / CALLER-OWNED LIFETIME EXPLICIT / FRAME-STYLE REUSE MEASURED / CARDINALITY + MEMORY MEASURED / REBUILD CHURN MEASURED / SHARED VS PARTITIONED MEASURED / TEARDOWN PASS / NO PERSISTENCE / NO NEW COLOR TRANSFORMATION`.

Evidence: `docs/runtime/cache/V1.42_RESOLUTION_CACHE_LIFETIME_CONTRACT__part_01.md` (split document; see adjacent parts), `docs/runtime/cache/V1.42_IMPLEMENTATION_REPORT_2026-09-27__part_01.md` (split document; see adjacent parts), `tools/audit_v142_resolution_cache_lifetime.py`, `tools/verify_v142_resolution_cache_lifetime.py`, `tools/benchmark_v142_resolution_cache_lifetime.py`, `tools/visual_qa_v142_resolution_cache_lifetime.py`, `artifacts/v142_resolution_cache_lifetime/`.

### V1.43 next micro-scope

1. identify the first actual production caller of `resolve_component()`;
2. map its object owner and destruction boundary;
3. determine whether it is renderer-, scene-, shot-, frame- or request-owned;
4. pass a real caller-owned `ResolutionCache` through that boundary;
5. measure actual frame reuse rather than the V1.42 diagnostic loop;
6. measure actual scene cardinality from the real owner;
7. measure actual retained memory and LRU churn;
8. test teardown of the real owner;
9. compare shared/partitioned behavior using actual simultaneous scenes;
10. add partitioning only if measured LRU pollution requires it;
11. add byte budgeting only if real memory evidence requires it;
12. add persistence only if a real restart/persistent consumer exists;
13. rerun V1.39–V1.42 cross-surface and concurrency gates;
14. preserve `ResolutionFingerprint.cache_identity` as the only semantic cache identity;
15. preserve the COLOR boundary unless a distinct real consumer is independently proven.

If no production consumer appears, V1.43 remains an audit/architecture checkpoint and does not invent an orchestration layer.

### V1.43 completion — first production consumer / ResolutionCache ownership

- [x] audit all 172 production Python files with alias-aware AST analysis
- [x] prove zero external production `resolve_component()` / `resolve_component_contract()` calls
- [x] prove zero production `ResolutionCache(...)` owners
- [x] audit RuntimeGraph production creation separately from generic resolution
- [x] audit renderer/frame/scene/shot orchestration without inventing a consumer
- [x] retain caller-owned cache contract
- [x] measure frame-style reuse using real production runtime classes, explicitly diagnostic
- [x] measure scene-adjacent `Frame`/`compose()` cardinality at 1 / 10 / 100 / 1,000 entities
- [x] measure retained Python memory with real Component/RuntimeGraph/resolution objects
- [x] measure RuntimeGraph rebuild churn at 32 / 128 / 512 components
- [x] compare shared and partitioned cache behavior with exact semantic identity reuse
- [x] verify teardown does not retain the authoring graph through cache results
- [x] verify no persistence/restart consumer exists
- [x] preserve `ResolutionFingerprint.cache_identity` as the sole semantic key
- [x] rerun cache/concurrency and COLOR regression surfaces
- [x] generate and manually inspect the production-consumer visual board
- [x] remove current V1.42 cache artifacts after evidence capture
- [x] preserve COLOR boundary

**V1.43 status:** `ENGINEERING PASS / AUDIT-ONLY / NO PRODUCTION CONSUMER / CALLER-OWNED CACHE / NO INVENTED ORCHESTRATION / MEMORY + REBUILD + SHARED/PARTITIONED EVIDENCE / TEARDOWN PASS / NO PERSISTENCE / COLOR UNCHANGED`.

### V1.44 next micro-scope

1. trace the first production entry point through the existing geometry/appearance/render vertical slice;
2. determine whether generic resolution is intentionally library-only or simply not wired into production;
3. identify any real caller if it appears and map its owner/destructor boundary;
4. if no caller appears, preserve the explicit architecture and do not create a cache manager;
5. only after a real caller exists measure real frame/scene lifetime, cardinality, memory, rebuild churn and LRU pollution;
6. revisit shared/partitioned ownership and byte budgets only from real workload evidence;
7. preserve `ResolutionFingerprint.cache_identity` as the sole semantic cache identity;
8. repeat single-flight, stale-graph, cross-surface and teardown tests after any integration;
9. preserve the COLOR boundary unless a distinct real consumer is independently proven.

### V1.44 completion — production vertical-slice audit — 2026-09-29

- [x] trace all 172 production Python files with AST-aware consumer analysis
- [x] exclude definitions/wrappers from external-consumer counts
- [x] resolve direct imports and aliases
- [x] prove zero external production generic-resolution callers
- [x] prove zero production geometry-generation service owners
- [x] prove zero production renderer callers
- [x] prove zero production entity-factory callers
- [x] audit ambiguous star imports and dynamic import/eval/exec surfaces
- [x] distinguish real spatial transform consumers from end-to-end orchestration
- [x] verify scene → runtime import direction remains empty
- [x] classify A8 as verification-only rather than production orchestration
- [x] execute A8 twice and confirm byte-identical evidence
- [x] generate and manually inspect a real renderer library-output sample
- [x] benchmark the audit tooling
- [x] compare production `src/` byte-for-byte against V1.43
- [x] preserve ResolutionCache caller-owned lifetime
- [x] preserve `ResolutionFingerprint.cache_identity`
- [x] preserve COLOR boundary
- [x] remove current V1.43 generated artifacts
- [x] rerun focused regression, full deterministic test batches and compileall

**V1.44 status:** `ENGINEERING PASS / NO PRODUCTION VERTICAL-SLICE CALLER / NO INVENTED ORCHESTRATION / A8 VERIFICATION-ONLY / NO SRC CHANGE / VISUAL QA PASS / COLOR UNCHANGED`.

### V1.45 next micro-scope — first real production generation/render slice

1. select one existing entity/component family with real geometry + renderer support;
2. define one explicit production request boundary and its owner/destructor;
3. connect the existing entity/component graph to RuntimeGraph without duplicating graph semantics;
4. connect appearance only where the selected asset actually needs it;
5. connect geometry generation through the existing registry/cache contracts;
6. connect spatial transform/placement/camera through the existing contracts;
7. invoke the real renderer and emit a real SVG/PNG artifact;
8. visually inspect coordinate orientation, clipping, child placement, appearance and determinism;
9. only then measure real cache lifetime, cardinality, memory, rebuild churn, LRU pressure and teardown;
10. add a caller-owned ResolutionCache only if the real request lifetime requires it;
11. rerun stale-graph, single-flight, cross-surface, visual-regression and COLOR gates;
12. do not add global managers, partitioning, byte budgets, persistence or new COLOR transforms without direct evidence.
