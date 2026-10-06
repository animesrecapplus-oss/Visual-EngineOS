<!-- Refactored from docs/governance/status/CURRENT_STATUS__part_01.md; source lines 278-408; content preserved. -->
<!-- Part 3/4. Use the family index for navigation. -->
## V1.44 — 2026-09-29 — production vertical-slice audit

V1.44 reoriented the execution frontier away from speculative infrastructure and toward the missing engine-wide production entry path. All 172 production Python files were AST-audited with alias handling, definition exclusion, export separation and ambiguity checks.

Findings:

- 0 external production `resolve_component()` / `resolve_component_contract()` calls;
- 0 production `CachedGeometryGenerator` owners;
- 0 production renderer callers;
- 0 production entity-factory callers;
- 0 audited star imports;
- 0 dynamic `__import__` / `eval` / `exec` calls;
- 0 scene → runtime imports;
- real spatial `resolve_geometry_contract()` consumers remain, but they are not a full production entity-to-render path;
- A8 remains a verification-only cross-layer harness, not a production renderer.

No production `src/` file changed. `ResolutionCache` remains caller-owned and `ResolutionFingerprint.cache_identity` remains its sole semantic identity. COLOR remains unchanged.

The complete V1.44 matrix contains 935 tests / 108 files: 934 passed, 1 expected PostgreSQL skip, 0 failed. `compileall` passed. The V1.44 gate is PASS.

**Current frontier:** build one real production-owned generation/render vertical slice before adding further cache/orchestration infrastructure.

## V1.45 — 2026-09-29 — first real production generation/render vertical slice

V1.45 closes the architectural gap identified by V1.44. A real caller-owned
`ProductionRenderSession` now executes the existing production contracts end-to-end for the
HumanFace family:

```text
build_human_face
  → RuntimeGraph
  → resolve_component + ResolutionCache
  → CachedGeometryGenerator + GeometryCache
  → face.human_with_eyes
  → resolve_geometry_contract
  → child appearance resolution
  → render_geometry_svg
  → SVG/PNG
```

The session is the first real production cache owner. It has an explicit `close()` boundary and
no global lifetime. Repeated real renders reuse the three geometry entries and three resolution
entries without rebuilding them.

A new generic SVG renderer was added with fail-closed support for paths and ellipses. Masks and
unknown primitive kinds are rejected. Geometry composition now rebases child path indexes and
preserves leaf ownership metadata.

Visual QA found and corrected a real paint-order defect before certification: the head had been
painted over the eye apertures. The accepted board contains front, +12° and -12° actual
production outputs and explicitly states that the current visual scope is head + two eyes;
nose/mouth/ears/hair are not falsely claimed as generated.

Validation:

```text
942 collected
941 passed
1 skipped (VISUAL_ENGINE_POSTGRES_DSN not configured)
0 failed
V1.31–V1.38 COLOR: 69 passed
V1.39–V1.45 cache/lifecycle: 71 passed
compileall: PASS
V1.45_PRODUCTION_VERTICAL_SLICE_GATE: PASS
```

The three canonical COLOR runtime files are byte-identical to V1.44. No new COLOR operation
was introduced. `ENGINE_VERSION=1.3.8`, `SCHEMA_VERSION=2`, `RESOLUTION_VERSION=20` remain
current.

The superseded current V1.44 generated artifact directory is removed. Historical V1.44
provenance remains in documentation/checkpoint form.

**Current frontier:** strengthen this real production slice before broadening the engine:
parallel sessions, real multi-instance cache pressure, one next missing face geometry family,
and the first genuine occlusion/visibility production integration.

## V1.46 — 2026-09-30 — strengthened first production slice

V1.46 is the second production-slice checkpoint. It does not generalize the engine broadly; it
proves the lifetime and visibility seams of the first real caller.

### Production path

```text
HumanFace
 → ProductionRenderSession
 → RuntimeGraph
 → resolve_component / ResolutionCache
 → CachedGeometryGenerator / GeometryCache
 → face.human_with_eyes_nose
 → spatial transform
 → generic SVG renderer
```

### What changed

- multiple simultaneous sessions are supported;
- injected caches are caller-owned and survive one session's `close()`;
- default-created caches remain session-owned and clear on `close()`;
- real concurrent shared/partitioned workloads were measured;
- no partitioning API was justified at the measured healthy working set;
- 1/2/4/8 live-session memory was measured before considering a new byte budget;
- exactly one new HumanFace family, `Nose`, was connected;
- the nose uses existing generic `VisualOverrides()` inheritance;
- resolved visibility/opacity now suppresses owned SVG geometry at zero;
- visual QA covers front, ±12° and visibility before/after;
- V1.45 generated artifacts were removed from the current checkpoint.

### Validation

Current repository: **110 test files / 950 tests; 949 passed, 1 expected PostgreSQL integration
skip, 0 failed**. `compileall` passes. The focused V1.31–V1.46 COLOR/cache/production family
contains 148 passing tests. V1.46 static audit reports 174 production Python files, 0 parse errors
and all checks passing. The production gate is PASS.

COLOR runtime files remain unchanged from V1.45. `ENGINE_VERSION=1.3.8`, `SCHEMA_VERSION=2` and
`RESOLUTION_VERSION=20` remain unchanged.

### Current evidence

`artifacts/v146_production_vertical_slice/` contains the V1.46 audit, multi-session workload
benchmark, gate, front/+12°/-12° SVG/PNG samples, visibility before/after samples and the manually
inspected runtime board. Superseded `artifacts/v145_production_vertical_slice/` is absent.

### Next frontier

V1.47 should integrate one real overlapping production component pair with the existing generic
visibility/occlusion kernel, including semantic regions, depth, blocked/visible area and direct
rendered-output comparison. No second new face family should be added before that evidence exists.
