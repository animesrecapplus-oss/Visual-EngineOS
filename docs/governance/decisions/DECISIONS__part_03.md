<!-- Refactored from docs/governance/decisions/DECISIONS__part_01.md; source lines 259-352; content preserved. -->
<!-- Part 3/3. Use the family index for navigation. -->
## D-089 — First production generation/render owner is an explicit caller-owned session — 2026-09-29

**Decision:** `ProductionRenderSession` is the first production owner of the generic resolution,
geometry generation and rendering lifetime.

**Reason:** V1.44 proved there was no production entity-to-render orchestration. V1.45 now creates
one real owner around the existing HumanFace contracts rather than introducing a global engine
manager.

**Rules:**

- the caller owns `ProductionRenderSession`;
- the session owns `RuntimeGraph`, `GeometryCache`, `ResolutionCache` and the geometry registry;
- `close()` is the explicit destruction boundary;
- no process/global cache is introduced;
- `ResolutionFingerprint.cache_identity` remains the sole semantic resolution-cache key;
- geometry cache identity remains owned by `GeometryCacheKey` / geometry fingerprints;
- stale `RuntimeGraph` state fails before rendering;
- unsupported generic SVG geometry fails closed;
- generic renderer presentation defaults are not COLOR transformations;
- no persistent render cache is introduced;
- no partitioning or new byte budget is introduced until real workload evidence requires it.

**Visual correction recorded:** the first V1.45 renderer draft painted the head after child eye
paths, hiding the eye apertures. The renderer was corrected to use explicit semantic paint order
and the visual board was regenerated before certification.

**Consequence:** the project now has a real production consumer, so the V1.42/V1.43 historical
zero-consumer assertions are superseded. Their historical reports remain unchanged; current tests
assert that `production_slice.py` is the only production owner.

**Version:** `ENGINE_VERSION=1.3.8`, `SCHEMA_VERSION=2`, `RESOLUTION_VERSION=20`.

## D-090 — V1.46 shared-cache lifetime, one new face family, and real visibility consumption — 2026-09-30

**Decision:** strengthen the first production slice without introducing a global manager. Multiple
`ProductionRenderSession` instances are allowed to share explicitly injected caches, but cache
ownership belongs to the caller that supplied them. Exactly one new HumanFace geometry family,
`Nose`, is connected through `face.human_with_eyes_nose`. Resolved zero visibility/opacity is
consumed by the generic SVG renderer.

**Evidence:** four simultaneous real production sessions were exercised with shared and partitioned
caches. With 16 entries—the complete active working set—both modes produced 16 geometry builds,
304 hits and 0 evictions. With 6 entries, the shared cache produced 308 builds, 12 hits and 302
evictions while partitioned caches produced 16 builds, 304 hits and 0 evictions. This demonstrates
LRU pollution from insufficient capacity, not a semantic requirement for partitioning.

**Lifecycle rule:** a session clears only caches it created. Injected `GeometryCache` and
`ResolutionCache` objects remain alive after one session closes so another live session can continue
using them. This fixes a concrete multi-owner lifetime hazard without introducing reference-counted
global state or a cache manager.

**Appearance rule:** the nose uses the existing generic `VisualOverrides()` inheritance contract.
No legacy `AppearanceLayer` → `VisualContract` translator is introduced because the legacy payload
is heterogeneous and the new consumer does not require such a bridge.

**Visibility rule:** V1.46 consumes resolved visibility/opacity at the generic renderer boundary.
It does not claim that SVG paint order is an occlusion solver. The existing renderer-independent
visibility kernel remains separate until one real overlapping production component pair justifies
its integration.

**Visual rule:** an initial nose prototype was rejected after direct visual inspection because it
was too elongated/leaf-like. The final geometry was shortened and redrawn before the certified
samples were generated.

**Invariants:** `ResolutionFingerprint.cache_identity` is unchanged; geometry cache identity remains
content-based; no persistence cache, global manager, partitioning API, new byte budget or COLOR
transformation is added.

**Next trigger:** one real overlapping production component pair must justify V1.47 visibility-kernel
integration before a second missing HumanFace family is connected.

## D-091 — V1.47 production visibility uses an explicit semantic path bridge — 2026-09-30

**Decision:** connect the first real production overlap as `HumanFace head <- Nose`, using the
existing renderer-independent visibility and attribution kernels, while keeping generic
`geometry_to_region()` primitive-only.

**Reasoning:** the production head and nose are closed Bézier paths, but the generic visibility
kernel intentionally consumes area primitives. Globally interpreting all closed renderer paths
would turn outlines/detail paths into accidental occluders and impose a cost on unrelated
workloads. The accepted boundary is therefore `explicit GeometrySurface -> closed path region ->
polygon primitive -> existing visibility kernel`.

**Depth semantics:** `depth_layer` is an explicit ordering layer, not a physical 3D coordinate.
V1.47 uses head layer 0 and nose layer 1. The implementation does not claim a z-buffer, ray tracing,
or continuous physical depth solution.

**Performance:** front occluder regions are materialized once per target region. No visibility cache
is introduced before a real workload establishes a lifetime and invalidation need.

**Rejected alternatives:** adding a second face geometry family; globally converting every path to
an area; adding a global visibility manager; adding a visibility cache; or changing COLOR without a
real consumer.
