<!-- Refactored from ['docs/history/implementation-log/IMPLEMENTATION_LOG__part_01.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_02.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_03.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_04.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_05.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_06.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_07.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_08.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_09.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_10.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_11.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_12.md']; source lines 1104-1244; content preserved. -->
<!-- Part 9/12. Use the family index for navigation. -->
### Next micro-scope — V1.44

1. trace the first production entry point through the existing geometry/appearance/render vertical slice;
2. determine whether generic resolution is intentionally library-only or simply not wired into production;
3. identify any real caller if it appears and map its owner/destructor boundary before injecting a cache;
4. if no caller appears, preserve the explicit architecture and do not invent an owner;
5. only after a real caller exists measure real frame/scene lifetime, cardinality, memory, rebuild churn and LRU pollution;
6. revisit shared/partitioned ownership and byte budgets only from real workload evidence;
7. preserve `ResolutionFingerprint.cache_identity` as the sole semantic cache identity;
8. repeat single-flight, stale-graph, cross-surface and teardown tests after any integration;
9. preserve the COLOR boundary unless a distinct real consumer is independently proven.

## V1.44 — 2026-09-29 — production vertical-slice audit / engine-wide reorientation

- Started strictly from the V1.43 certified checkpoint. The objective was to trace the first real production entry through the existing entity/component → resolution → geometry → spatial → renderer surfaces, not to extend COLOR or invent another cache manager.
- Parsed all 172 production Python files with an AST-based audit. Direct imports and aliases are resolved; calls inside defining modules are excluded from downstream-consumer counts; public exports are recorded separately.
- Added ambiguity checks for star imports from audited surfaces and dynamic `__import__` / `eval` / `exec` calls. Final result: zero ambiguous star imports and zero dynamic import/eval/exec calls.
- Confirmed zero external production calls to `resolve_component()` / `resolve_component_contract()`; zero production `CachedGeometryGenerator` owners; zero production renderer callers; zero production entity-factory callers.
- Kept real `resolve_geometry_contract()` calls in spatial subsystems classified as spatial consumers rather than falsely promoting them to an end-to-end production vertical slice.
- Audited scene dependency direction. `scene` imports no runtime module; runtime uses scene composition data only. No scene-owned generic resolution or render orchestration exists.
- Audited the existing A8 cross-layer verifier separately. A8 is explicitly a verification harness, not a production rendering engine. It remains outside `src/` and is not counted as a production consumer.
- Executed A8 twice from clean output directories. Both reports are byte-identical and preserve the same geometry, resolution, serialization and SVG digests. Temporary run directories are deleted after evidence capture.
- Generated an actual renderer sample through the existing ocular renderer. The V1.44 board labels it as a library API sample and does not represent it as a production call. The board was manually inspected; an initial text-overlap issue was corrected before final evidence capture.
- Benchmarked the audit tooling over five clean subprocess runs: median 1.7523 s, minimum 1.6518 s, maximum 2.0271 s. This is tooling performance only, not a production runtime benchmark.
- Compared every production `src/**/*.py` file against V1.43: zero production source changes.
- Created: `tools/audit_v144_production_vertical_slice.py`, `tools/benchmark_v144_production_vertical_slice.py`, `tools/visual_qa_v144_production_vertical_slice.py`, `tools/verify_v144_production_vertical_slice.py`, `tests/unit/test_v144_production_vertical_slice.py`, `docs/runtime/production/V1.44_PRODUCTION_VERTICAL_SLICE_AUDIT_CONTRACT__part_01.md` (split document; see adjacent parts), `docs/runtime/production/V1.44_IMPLEMENTATION_REPORT_2026-09-29__part_01.md` (split document; see adjacent parts), and `artifacts/v144_production_vertical_slice/` evidence.
- Modified: `README.md`, `docs/history/implementation-log/IMPLEMENTATION_LOG__part_01.md` (split document; see adjacent parts), `docs/governance/decisions/DECISIONS__part_01.md`, `docs/governance/status/CURRENT_STATUS__part_01.md`, `docs/governance/roadmap/ROADMAP__part_01.md`.
- No production `src/` file was modified.
- The V1.43 current generated artifact directory is removed from the V1.44 release tree after its historical report/checkpoint was retained.
- Full repository collection now contains 935 tests across 108 test files. The complete matrix was executed to completion in deterministic batches: 934 passed, 1 expected PostgreSQL skip, 0 failed. `compileall` passed.
- Focused V1.39–V1.44/cache + COLOR regression family passed with 68 tests and 0 failures.
- V1.44 gate: `V1.44_PRODUCTION_VERTICAL_SLICE_GATE: PASS`.

**V1.44 result:** `ENGINEERING PASS / NO PRODUCTION VERTICAL-SLICE CALLER / NO INVENTED ORCHESTRATION / A8 VERIFICATION-ONLY / NO SRC CHANGE / VISUAL QA PASS / DETERMINISTIC A8 PASS / COLOR UNCHANGED`.

### V1.45 next micro-scope

1. choose one real supported entity/component production asset;
2. create one explicit production request boundary;
3. wire only the existing entity → RuntimeGraph → appearance/geometry → spatial → renderer contracts that the selected asset actually needs;
4. determine whether generic resolution is truly required rather than forcing it into the path;
5. establish real ownership and teardown before introducing any cache manager;
6. generate a real SVG/PNG asset and visually inspect it for coordinate, clipping, appearance and placement failures;
7. measure real request reuse, graph rebuild, cache cardinality, retained memory and teardown only after the path is real;
8. rerun stale-graph, single-flight, cross-surface, visual and COLOR regression gates;
9. do not introduce partitioning, byte budgets, persistence, new COLOR transforms or global managers without evidence.

## V1.45 — First real production generation/render vertical slice — 2026-09-29

### Trigger

V1.44 proved that the repository had no production-owned entity → resolution → geometry →
spatial → renderer path. V1.45 therefore moved from audit-only work to one explicit production
caller using the existing `HumanFace` family.

### Implemented

- created `ProductionRenderSession` as the first caller-owned production lifetime;
- connected `RuntimeGraph.from_component()`;
- connected the existing `resolve_component()` and `ResolutionCache`;
- connected the existing `CachedGeometryGenerator` / `GeometryCache`;
- connected the existing `face.human_with_eyes` composite generator;
- connected `resolve_geometry_contract()` for placement/camera transforms;
- created a fail-closed generic `GeometryContract` → SVG renderer;
- connected child component appearance through existing generic resolution;
- added explicit session teardown and refresh semantics;
- generated actual SVG + PNG samples from the production session;
- manually inspected front/+12°/-12° outputs;
- caught and corrected two visual/ownership defects before certification:
  1. head surface owner was synthetic rather than the requested face id;
  2. paint order caused the head to cover eye apertures;
- preserved `ResolutionFingerprint.cache_identity` unchanged;
- preserved the COLOR boundary byte-for-byte.

### Geometry metadata correction

`components/common/geometry_composition.py` now rebases child-local `path_index` values to
parent-global indexes and preserves the original leaf owner in `source_component_id`.
This is required by the generic renderer and prevents path-role ambiguity in nested composites.

### Appearance correction

`entities/face.py` now gives the existing HumanFace builder an explicit authored
`VisualContract` so the generic resolver remains the appearance authority. The new renderer
does not parse legacy appearance-layer color payloads.

### Validation

- 942 tests collected;
- 941 passed;
- 1 expected PostgreSQL skip;
- 0 failed;
- V1.31–V1.38 COLOR family: 69 passed;
- V1.39–V1.45 cache/lifecycle family: 71 passed;
- deterministic 10-batch repository execution: all batches PASS;
- integration suite: 4 passed / 1 expected PostgreSQL skip;
- compileall: PASS;
- `V1.45_PRODUCTION_VERTICAL_SLICE_GATE: PASS`.

The monolithic pytest invocation was attempted but exceeded the outer execution window at
84%; it is not treated as a test failure because every test file was subsequently completed
in deterministic batches.

### Evidence

Current generated evidence:

`artifacts/v145_production_vertical_slice/`

Includes source audit, runtime benchmark, gate, three SVG/PNG render variants and a manually
inspected runtime board.

### Source files

Created:

- `src/visual_engine/render/geometry_svg.py` — 204 lines;
- `src/visual_engine/runtime/production_slice.py` — 165 lines.

Modified:

- `src/visual_engine/components/common/geometry_composition.py` — global surface indexes + owner preservation;
- `src/visual_engine/components/face/generators.py` — actual head owner metadata;
- `src/visual_engine/entities/face.py` — authored `VisualContract`;
- `src/visual_engine/render/__init__.py` — generic renderer export;
- `src/visual_engine/runtime/__init__.py` — production session export.

Tests modified for the now-superseded V1.42/V1.43 zero-consumer assertions:

- `tests/unit/test_v142_resolution_cache_lifetime.py`;
- `tests/unit/test_v143_production_consumer_audit.py`.

### Tools

Created:

- `tools/audit_v145_first_production_slice.py` — 84 lines;
- `tools/benchmark_v145_production_vertical_slice.py` — 95 lines;
- `tools/visual_qa_v145_production_vertical_slice.py` — 101 lines;
- `tools/verify_v145_production_vertical_slice.py` — 48 lines.
