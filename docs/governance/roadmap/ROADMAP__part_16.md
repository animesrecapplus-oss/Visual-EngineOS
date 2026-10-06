<!-- Refactored from docs/governance/roadmap/ROADMAP__part_01.md; source lines 2003-2112; content preserved. -->
<!-- Part 16/16. Use the family index for navigation. -->
### V1.45 completion — first real production generation/render vertical slice — 2026-09-29

- [x] select an existing entity family with real geometry contracts
- [x] create one explicit caller-owned production render boundary
- [x] compile the authoring entity into RuntimeGraph in production
- [x] connect generic component resolution to the real owner
- [x] connect ResolutionCache at the real owner lifetime
- [x] connect existing geometry registry/cache through the real owner
- [x] connect the existing HumanFace composite generator
- [x] connect real spatial placement/camera transformation
- [x] create a generic GeometryContract SVG renderer rather than a second eye renderer
- [x] preserve component appearance ownership in the generic resolver
- [x] correct composite surface path indexes and leaf ownership metadata
- [x] verify stale graph failure and refresh behavior
- [x] verify explicit session teardown
- [x] measure real warm cache reuse
- [x] measure real warm render timing
- [x] measure one-session memory
- [x] generate actual SVG + PNG production samples
- [x] visually inspect front/+12°/-12° outputs
- [x] reject and correct the first visually incorrect paint-order implementation
- [x] run focused COLOR regression
- [x] run V1.39–V1.45 cache/lifecycle regression
- [x] execute all test files to completion in deterministic batches
- [x] compile all source/tests/tools
- [x] preserve COLOR boundary
- [x] remove superseded current V1.44 generated artifacts

**V1.45 status:** `ENGINEERING PASS / FIRST REAL PRODUCTION OWNER / CALLER-OWNED SESSION /
REAL CACHE REUSE / SPATIAL TRANSFORM / GENERIC SVG RENDERER / FAIL-CLOSED / TEARDOWN PASS /
VISUAL QA PASS / COLOR UNCHANGED`.

### V1.46 — first production slice strengthened — 2026-09-30

- [x] prove multiple simultaneous `ProductionRenderSession` owners;
- [x] distinguish session-owned from caller-injected shared caches;
- [x] run real concurrent shared-vs-partitioned cache workloads;
- [x] measure LRU pollution before considering partitioning;
- [x] measure 1/2/4/8-instance retained memory before considering a new byte budget;
- [x] inspect the generic appearance boundary;
- [x] use the existing `VisualOverrides` inheritance contract for the new nose;
- [x] add exactly one new HumanFace geometry family (`Nose`);
- [x] connect `face.human_with_eyes_nose` to the production session;
- [x] consume resolved visibility/opacity in the generic renderer;
- [x] generate before/after visibility evidence;
- [x] repeat stale graph, cache, teardown, determinism and visual gates;
- [x] preserve `ResolutionFingerprint.cache_identity`;
- [x] keep COLOR frozen;
- [x] remove superseded V1.45 current generated artifacts.

**V1.46 status:** `ENGINEERING PASS / MULTI-SESSION OWNER / SHARED-CACHE LIFETIME FIX /
ONE NEW FACE FAMILY / REAL VISIBILITY CONSUMER / SHARED-VS-PARTITIONED MEASURED /
MEMORY MEASURED / VISUAL QA PASS / COLOR UNCHANGED`.

### V1.47 next micro-scope — one real overlapping production visibility path

1. select exactly one genuinely overlapping production component pair;
2. connect the existing renderer-independent visibility kernel to the production request boundary;
3. materialize semantic regions and explicit depth for the pair;
4. prove blocked area, visible area, dominant occluder and depth relation;
5. compare those results against the actual rendered output;
6. generate before/after visual evidence;
7. measure visibility cost before adding a cache;
8. repeat multi-session/cache/lifecycle/determinism/visual regression gates;
9. preserve `ResolutionFingerprint.cache_identity`;
10. keep COLOR frozen unless a real downstream consumer proves a missing contract.

Do not add a second missing HumanFace geometry family until this overlap path is proven.


### V1.47 completion — first real production visibility overlap — 2026-09-30

- [x] verify the roadmap/vision before implementation and confirm no skipped V1.46 item;
- [x] select exactly one genuinely overlapping production pair (`head <- nose`);
- [x] close the path-to-area semantic gap without changing global renderer path semantics;
- [x] materialize semantic regions from explicit closed surfaces;
- [x] fail closed on unsupported path topology/holes;
- [x] author explicit depth layers for the pair;
- [x] connect the real camera-space production geometry to `resolve_visibility`;
- [x] connect the same request to `resolve_visibility_attribution`;
- [x] prove blocked area, visible area, dominant occluder and depth relation;
- [x] compare the exact kernel region with rasterized production geometry;
- [x] generate front/+12°/-12° raw production samples;
- [x] manually inspect the visual board and reject semantic/render mismatches;
- [x] measure visibility cost before adding a visibility cache;
- [x] optimize repeated occluder-region conversion and remeasure;
- [x] rerun production lifecycle/cache/determinism/visual regression gates;
- [x] run all 111 test files / 956 collected tests in isolated batches;
- [x] preserve `ResolutionFingerprint.cache_identity`;
- [x] keep COLOR frozen and byte-identical to V1.46;
- [x] remove superseded V1.46 current generated artifacts.

**V1.47 status:** `ENGINEERING PASS / HEAD-NOSE PRODUCTION VISIBILITY / SEMANTIC REGION BRIDGE /
EXPLICIT DEPTH / ATTRIBUTION / VISUAL QA PASS / PERFORMANCE PASS / COLOR UNCHANGED`.

### V1.48 completion — controlled source modularization audit — 2026-09-30

- [x] inventory every production Python module above 150 lines;
- [x] build the direct source import graph and check cycles;
- [x] scan exact duplicate function bodies;
- [x] manually inspect high-similarity duplicate candidates;
- [x] select one module from a real responsibility seam;
- [x] extract planar-region materialization from `runtime.visibility`;
- [x] preserve legacy/public import identities;
- [x] add adversarial ownership and deterministic-conversion tests;
- [x] benchmark baseline versus refactored source in fresh processes;
- [x] run complete regression after cleanup;
- [x] purge generated current/history/release artifacts;
- [x] preserve COLOR and renderer behavior unchanged.

**V1.48 status:** `ENGINEERING PASS / ONE SOURCE RESPONSIBILITY EXTRACTED / API COMPATIBLE /
NO VISUAL SEMANTIC CHANGE / ARTIFACT RETENTION CLEANED`.

### V1.49 completion — controlled GeometryContract transformation extraction — 2026-09-30

- [x] audit dependency graph, responsibilities, consumers, cycles and duplicate candidates before extraction;
- [x] select exactly one module: `runtime.geometry_transform`;
- [x] select exactly one responsibility: renderer-independent GeometryContract coordinate transformation;
- [x] create one implementation owner and preserve public/legacy API identity;
- [x] move real consumers to the owner without changing semantic contracts;
- [x] add ownership, adversarial, API and dependency-boundary tests;
- [x] run complete regression and verify the three known SCCs remain unchanged;
- [x] benchmark the seam and the warm production render against V1.48;
- [x] compare a real production SVG and inspect the rendered PNG;
- [x] retain only the current V1.49 evidence under `artifacts/current/v1.49/`;
- [x] update bounded history, status, decision and artifact-retention documentation;
- [x] produce the V1.49 certified checkpoint ZIP outside the project tree.

**V1.49 status:** `ENGINEERING PASS / ONE SOURCE RESPONSIBILITY EXTRACTED / API COMPATIBLE / CYCLE SAFE /
FULL REGRESSION PASS / PERFORMANCE PASS / SVG BYTE-IDENTICAL / CURRENT ARTIFACT RETAINED`.

### V1.50 next micro-scope

1. repeat the dependency graph from the V1.49 certified tree;
2. inventory remaining oversized modules by actual responsibility, not line count;
3. trace production consumers before choosing a seam;
4. repeat exact and high-similarity duplicate detection with manual false-positive review;
5. select exactly one module and one independent responsibility;
6. extract one owner only, with API/cycle/adversarial tests;
7. benchmark the affected production path against V1.49;
8. compare real visual output when the seam can change geometry/rendering;
9. keep COLOR frozen unless a real downstream consumer proves a missing contract;
10. purge superseded V1.49 generated evidence while retaining the `artifacts/` directory and the current
    V1.50 evidence;
11. update exact file/line history and deliver one new certified ZIP.
12. do not split merely to satisfy the 150-line inventory threshold.
