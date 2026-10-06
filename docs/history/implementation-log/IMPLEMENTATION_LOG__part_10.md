<!-- Refactored from ['docs/history/implementation-log/IMPLEMENTATION_LOG__part_01.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_02.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_03.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_04.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_05.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_06.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_07.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_08.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_09.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_10.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_11.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_12.md']; source lines 1245-1386; content preserved. -->
<!-- Part 10/12. Use the family index for navigation. -->
### Documentation

Created:

- `docs/runtime/production/V1.45_PRODUCTION_VERTICAL_SLICE_CONTRACT__part_01.md` (split document; see adjacent parts);
- `docs/runtime/production/V1.45_IMPLEMENTATION_REPORT_2026-09-29__part_01.md` (split document; see adjacent parts).

Updated:

- `README.md`;
- `docs/history/implementation-log/IMPLEMENTATION_LOG__part_01.md` (split document; see adjacent parts);
- `docs/governance/decisions/DECISIONS__part_01.md`;
- `docs/governance/status/CURRENT_STATUS__part_01.md`;
- `docs/governance/roadmap/ROADMAP__part_01.md`.

### Version policy

`ENGINE_VERSION=1.3.8`, `SCHEMA_VERSION=2`, `RESOLUTION_VERSION=20` remain unchanged.
V1.45 adds production orchestration and renderer coverage but does not change schema or
resolution identity semantics.

### Next micro-scope

V1.46 must strengthen the real production slice before generalizing it: parallel/independent
sessions, real multi-instance cache pressure, appearance bridge gaps only when demonstrated,
one next missing face geometry family, and the first real occlusion/visibility integration.
No new global manager, persistence cache, byte budget or COLOR transform should be added without
measurement from the real production workload.

## V1.46 — First production slice strengthened — 2026-09-30

### Trigger

V1.45 had established one real `ProductionRenderSession` owner but had not yet proved the
lifetime semantics of multiple simultaneous owners. The first missing HumanFace geometry family
also remained unconnected, and resolved visibility was not yet consumed by the generic SVG
emitter.

### Implementation

1. Measured multiple live sessions with the actual `ProductionRenderSession.render_face()` path.
2. Found a real ownership defect: a session always cleared an injected cache during `close()`,
   which is unsafe when two sessions share that cache.
3. Added explicit `_owns_geometry_cache` and `_owns_resolution_cache` flags. Default-created
   caches remain session-owned; injected caches remain caller-owned.
4. Added exactly one new geometry family, `Nose`, with the existing `GeometryContract` and
   `RegisteredGeometryGenerator` contracts.
5. Added `face.human_with_eyes_nose` as the explicit composite production generator and made it
   the default production request for `render_face()`.
6. Added nose geometry as one closed silhouette plus two open nostril curves. No mask, shading,
   boolean or COLOR operation was invented.
7. Used the existing `VisualOverrides()` field-level inheritance contract on the nose so its
   appearance follows the authored HumanFace `VisualContract` instead of duplicating a color
   authority.
8. Changed the generic SVG renderer to omit geometry whose resolved visibility or effective
   opacity is zero. Existing fail-closed mask/primitive/XML behavior remains unchanged.
9. Ran actual concurrent four-session shared and partitioned workloads at healthy and deliberately
   undersized capacities.
10. Measured retained memory for 1/2/4/8 simultaneous production sessions before considering a
    new byte budget.
11. Generated actual SVG/PNG front, +12°, -12° and visibility before/after samples.
12. Manually inspected the generated board and rejected an earlier nose shape because it was too
    elongated and leaf-like; the final silhouette was reduced and redrawn before evidence capture.

### Evidence-based decisions

- No cache partitioning: with the complete 16-key working set, shared and partitioned caches both
  produced 16 builds / 304 hits / 0 evictions. With only 6 entries, shared cache pollution was
  visible (308 builds / 12 hits / 302 evictions) while partitioned caches retained 16 builds / 304
  hits / 0 evictions. This is capacity pressure, not a justification for a partitioning API.
- No new memory budget: measured retained memory and geometry payload scale with live instances;
  existing cache bounds remain the explicit controls.
- No legacy AppearanceLayer bridge: the new nose can use the already-typed generic inheritance
  contract safely. Translating heterogeneous legacy appearance payloads would be speculative.
- No full occlusion implementation: V1.46 makes visibility real at the renderer boundary. The
  existing renderer-independent occlusion kernel is not falsely wired into draw order without a
  concrete overlapping production component.
- COLOR remains frozen and byte-identical to V1.45.

### Files created

- `docs/runtime/production/V1.46_PRODUCTION_SLICE_CONTRACT__part_01.md` (split document; see adjacent parts)
- `docs/runtime/production/V1.46_IMPLEMENTATION_REPORT_2026-09-30__part_01.md` (split document; see adjacent parts)
- `tests/unit/test_v146_production_slice.py`
- `tools/audit_v146_production_slice.py`
- `tools/benchmark_v146_multi_session.py`
- `tools/visual_qa_v146_production_slice.py`
- `tools/verify_v146_production_slice.py`
- `artifacts/v146_production_vertical_slice/*` evidence
- `artifacts/releases/v1.46/evidence.txt`
- `artifacts/releases/v1.46/manifest.json`

### Production files modified

- `src/visual_engine/components/face/generators.py` — nose generator, nose dependency and
  `face.human_with_eyes_nose` composite.
- `src/visual_engine/entities/face.py` — typed nose parameters and generic `VisualOverrides()`
  inheritance.
- `src/visual_engine/render/geometry_svg.py` — nose closed-path role and resolved visibility /
  opacity emission gate.
- `src/visual_engine/runtime/production_slice.py` — new default composite generator and explicit
  cache ownership semantics.

### Historical test maintenance

- `tests/unit/test_v144_production_vertical_slice.py` no longer reads the deleted V1.44 generated
  artifact directory; it validates the retained historical report instead.
- `tests/unit/test_v145_production_vertical_slice.py` now reflects V1.46 injected-cache ownership:
  caller-injected caches survive session close.

### Validation

- 110 test files / 950 collected tests.
- First deterministic execution partition: 757 tests, 756 passed, 1 expected PostgreSQL skip.
- Second deterministic execution partition: 193 tests, 193 passed, 0 failed.
- Aggregate: **949 passed / 1 expected PostgreSQL skip / 0 failed**.
- V1.31–V1.46 focused COLOR/cache/production family: 148 passed / 0 failed.
- `python -m compileall -q src tests tools`: PASS.
- Static V1.46 audit: 174 production Python files, 0 parse errors, all checks PASS.
- V1.46 production gate: `V1.46_PRODUCTION_VERTICAL_SLICE_GATE: PASS`.

The monolithic and highly parallel repository runners were also attempted but hit the outer
execution window. They were not used as evidence of success or failure. The final acceptance
numbers above come from completed fresh pytest executions covering all 110 test files.

### Current artifacts

`artifacts/v145_production_vertical_slice/` is removed from the V1.46 current tree. Historical
V1.45 reports remain intact. Current generated evidence is under:

`artifacts/v146_production_vertical_slice/`

### Next micro-scope

V1.47 should address one genuinely overlapping production component pair and connect the existing
renderer-independent visibility kernel to the production request boundary. It must prove semantic
regions, depth relation, blocked/visible area and rendered result agree before adding another face
family. Visibility cost should be measured before caching it. Multi-session/cache/lifecycle,
determinism, visual regression and COLOR gates remain mandatory.

## V1.47 — Production visibility path: head ← nose — 2026-09-30
