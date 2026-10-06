<!-- Refactored from docs/governance/decisions/DECISIONS__part_01.md; source lines 143-258; content preserved. -->
<!-- Part 2/3. Use the family index for navigation. -->
## D-V1.38 — 2026-09-25 — Close effect-color provenance/invalidation before inventing another operation

**Decision:** V1.38 keeps `effect.color.srgb8-interpolation` as the sole RGB operation. The existing path is strengthened only where the audit found real semantic closure defects: cumulative multi-effect lineage and complete effect-color dependency fingerprinting.

**Reason:** the audit proved that fill/contour and successive effects were real production paths. A second color-space operation would have been unsupported. The correct next action was to make the existing operation's provenance and invalidation semantics complete.

**Invariant:** `VisualEffect.alpha` is the sole RGB-effect alpha authority; `effect.color.alpha` is ignored; effects execute in `(priority, effect_id, source_id)` order; duplicate effect IDs fail closed; actual effect color always participates in the dependency fingerprint; operation version participates in invalidation; no hidden HSL/OKLab/XYZ/gamut/compositing operation is allowed inside `effect_color`.

**Version:** `ENGINE_VERSION=1.3.8`, `SCHEMA_VERSION=2`, `RESOLUTION_VERSION=19`. The resolution identity changes because cache/invalidation/provenance semantics changed, not because a new RGB transformation was added.

**Boundary:** no saturation, contrast, vibrance, lightness, temperature, palette mixing, lighting, shading, material response, gamut mapping or new color space is introduced by V1.38.

## D-083 — Resolution cache identity is the existing ResolutionFingerprint, not a second dependency system

V1.39 establishes the cache boundary below `resolve_component()` and above the existing resolution fingerprint. The production cache key is exactly `ResolutionFingerprint.cache_identity`; the cache does not inspect effect fields, relation metadata, colors or state fields independently.

**Reason:** duplicating dependency logic in a cache would create two invalidation authorities and eventually allow drift. The existing `dependency_fingerprint + VersionStamp + context_fingerprint` structure already defines the semantic identity required by resolution.

**Implementation:** add an optional bounded `ResolutionCache` to `resolve_component()` and `resolve_component_contract()`. Hits return immutable `ResolvedComponent` instances; misses execute the authoritative resolver and then store the result.

**Invariant:** changed resolution dependency ⇒ different cache identity; unchanged canonical dependency ⇒ same cache identity. Input insertion order is not semantic when canonical precedence is unchanged. Duplicate effect IDs fail closed.

**Additional correction:** `state_priority` is omitted from the targeted context fingerprint when no context states are active because it cannot affect resolution in that case. This is a deliberate false-invalidation correction, not a weakening of active-state invalidation.

**Version:** `ENGINE_VERSION=1.3.8`, `SCHEMA_VERSION=2`, `RESOLUTION_VERSION=20`.

**Boundary:** V1.39 adds no color-space operation and does not modify the existing `effect.color.srgb8-interpolation` law.

## D-084 — ResolutionCache remains caller-owned; graph freshness stays RuntimeGraph-owned — 2026-09-26

**Decision:** V1.40 does not introduce a global, scene-owned or process-owned `ResolutionCache`. Repository AST evidence found zero production cache constructions; current production use is optional dependency injection from callers.

**Reason:** cache lifetime must be based on an actual owner. Inventing a global cache would create an unproven lifecycle policy and would complicate invalidation across mutable `RuntimeGraph` instances.

**Implementation:** when a cache is supplied, `resolve_component()` explicitly checks `RuntimeGraph.is_current()` before calculating/looking up the cache identity. Stale graphs fail closed and must be rebuilt. Rebuilt graphs reuse entries when the target's existing `ResolutionFingerprint.cache_identity` is unchanged.

**Invariant:** `RuntimeGraph` owns structural freshness; `ResolutionFingerprint` owns semantic resolution identity; `ResolutionCache` owns bounded entry storage and LRU behavior. No second dependency system is introduced.

**Cross-surface rule:** resolution and geometry caches may share hierarchy/relation topology dependencies but retain separate semantic ownership. Visual-only mutations belong to resolution; explicit geometry inputs belong to geometry; arbitrary visual relation-effect metadata does not become geometry identity.

**Concurrency:** the existing `RLock` is sufficient for entry/counter consistency. Single-flight build coalescing remains deliberately unimplemented until duplicate-build measurements justify it.

**Statistics:** `ResolutionCache.stats` is already an immutable snapshot. No reset API is added in V1.40; fresh cache instances provide isolated measurement windows.

**Persistence:** no serialized cache/fingerprint envelope is implemented because no persistent cache consumer exists. If persistence becomes real, a versioned envelope must be specified before storage is introduced.

**Version:** `ENGINE_VERSION=1.3.8`, `SCHEMA_VERSION=2`, `RESOLUTION_VERSION=20`. No resolution identity semantics changed in V1.40.

**Boundary:** no new color operation is introduced and `effect.color.srgb8-interpolation` remains the sole existing generic color transformation.

## D-085 — ResolutionCache coalesces only identical concurrent fingerprints — 2026-09-27

V1.41 establishes `ResolutionCache.get_or_build()` as the production build boundary. A
same-key concurrent MISS is coalesced through a per-fingerprint in-flight state; unrelated
fingerprints remain independently buildable. The resolver's authoritative computation is
kept separate in `_resolve_component_uncached()`.

This decision was evidence-driven: a forced real resolver race reproduced one redundant
build per concurrent caller before the change. After the change, 2/4/8/16/32 concurrent
callers produce one build and the same immutable result object. Builder failures are
published to current waiters and do not create cache entries.

`clear()` is a lifecycle generation boundary. An active pre-clear build may finish for its
current waiters but cannot repopulate the newly cleared cache, and new callers cannot join
the old in-flight registry.

No global cache owner, frame cache, scene cache, persistence envelope or telemetry system
is introduced because no real production consumer currently requires one. `ResolutionFingerprint.cache_identity`
remains the only cache identity and `RuntimeGraph` remains the topology freshness authority.

## D-086 — ResolutionCache stays caller-owned until a real production owner exists — 2026-09-27

V1.42 searched the production source graph for the first real owner of `ResolutionCache` and found none. There are zero production cache constructions and zero downstream production calls to the generic resolver. The renderer consumes eye geometry/appearance directly, while the scene module exposes composition data without owning generic resolution.

**Decision:** keep `ResolutionCache` caller-owned and optional. Do not introduce a global, process, scene, frame or renderer cache manager merely to give the cache an owner.

**Evidence:** a diagnostic workload using production `Component`, `RuntimeGraph`, `resolve_component()` and `ResolutionCache` demonstrated 32 first-frame misses followed by 1,888 hits over 59 unchanged rebuilt graph boundaries. This is evidence of cache capability, not evidence of an existing production frame loop.

**Shared/partitioned:** exact-identical independent graphs reused 32 entries through one shared cache but could not reuse across two partitioned caches. Distinct graphs under equal total capacity produced the same miss/hit result under the tested alternating workload. No partitioning API is therefore justified yet.

**Teardown:** cached `ResolvedComponent` results do not retain the authoring `Component` tree or `RuntimeGraph`; a unique production component tree was garbage-collected while its cache entry remained alive.

**Persistence:** no production fingerprint persistence consumer exists. No serialized fingerprint/cache envelope is introduced.

**Invariant:** `ResolutionFingerprint.cache_identity` remains the sole semantic cache identity; `RuntimeGraph` remains the structural freshness authority; `ResolutionCache` remains the bounded storage/concurrency owner.

**COLOR boundary:** unchanged; no color operation is introduced.

## D-087 — Do not invent a ResolutionCache owner before the first real resolver consumer — 2026-09-28

V1.43 audited all 172 production Python files with alias-aware AST analysis and found zero external calls to `resolve_component()` / `resolve_component_contract()` and zero production `ResolutionCache(...)` constructions.

**Decision:** V1.43 remains audit-only. `ResolutionCache` stays caller-owned and optional. No renderer, scene, shot, frame, request, process or global owner is introduced.

`RuntimeGraph.from_component()` in persistence is a graph compilation/validation boundary, not a generic resolution consumer. `Frame`/`Shot`/`compose()` provide composition data, while the SVG renderer consumes `EyeGeometry`/`EyeAppearance` directly.

Diagnostic frame-style and shared-cache measurements are explicitly non-production evidence. They demonstrate capability but do not justify an orchestration layer, partitioning API, byte budget or persistence envelope.

**Invariant:** `ResolutionFingerprint.cache_identity` remains the sole semantic resolution-cache identity; `RuntimeGraph` remains the structural freshness authority.

**COLOR boundary:** unchanged. No color runtime file or transformation is introduced.

## D-088 — Do not confuse verification vertical slices with production orchestration — 2026-09-29

**Decision:** V1.44 does not promote the existing A8 end-to-end verifier into production and does not create a production scene/render manager.

**Evidence:** all 172 production Python files were AST-audited. There are zero external production `resolve_component()` / `resolve_component_contract()` callers, zero production `CachedGeometryGenerator` owners, zero production renderer callers and zero production entity-factory callers. The only complete cross-layer path is `tools/verify_a8_e2e.py`, whose own contract explicitly identifies it as an integration verification harness.

**Reason:** treating A8 as production would create a false architectural positive and would force unproven ownership/lifetime rules. Public library exports are not production consumers. Spatial `resolve_geometry_contract()` calls are real but do not constitute an entity-to-render vertical slice.

**Invariant:** `ResolutionCache` remains caller-owned; `ResolutionFingerprint.cache_identity` remains the sole semantic cache identity; `RuntimeGraph` remains the topology freshness authority. No scene/frame/request/global cache owner is invented.

**COLOR boundary:** unchanged. V1.44 introduces no color transformation and no COLOR runtime modification.

**Next trigger:** a real production-owned generation/render request must appear before cache lifetime or broader orchestration is changed.
