<!-- Refactored from ['docs/history/implementation-log/IMPLEMENTATION_LOG__part_01.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_02.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_03.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_04.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_05.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_06.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_07.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_08.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_09.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_10.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_11.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_12.md']; source lines 1387-1518; content preserved. -->
<!-- Part 11/12. Use the family index for navigation. -->
### Roadmap compliance gate before implementation

V1.47 was not started as a free-form geometry addition. The current roadmap was read first and
compared with the V1.46 checkpoint. The documented V1.47 micro-scope explicitly required:

1. exactly one genuinely overlapping production component pair;
2. connection of the existing renderer-independent visibility kernel to the production request
   boundary;
3. semantic regions and explicit depth for the pair;
4. blocked area, visible area, dominant occluder and depth relation;
5. comparison with the actual rendered output;
6. visual before/after evidence;
7. visibility-cost measurement before any visibility cache;
8. repetition of lifecycle/cache/determinism/visual gates;
9. preservation of `ResolutionFingerprint.cache_identity`;
10. COLOR frozen unless a real downstream consumer proves a missing contract.

The selected pair is `HumanFace head <- Nose`. The nose is already a real production component from
V1.46, it geometrically overlaps the head, and no second face geometry family is introduced in V1.47.
No mouth/ear/hair generator is added.

### Initial contract audit and rejected shortcut

The existing visibility kernel accepted area primitives (polygon/ellipse/circle), while the real
V1.46 head and nose are renderer-neutral closed Bézier paths. Connecting those paths by changing
`geometry_to_region()` to interpret every closed path globally was tested and rejected: it would
make ordinary renderer/detail paths into implicit area geometry and substantially increase the cost
of unrelated visibility calls. This was an actual architecture/performance regression, not merely
aesthetic preference.

The final solution keeps the generic kernel primitive-only and adds an explicit path-region bridge:
only a `GeometrySurface` that explicitly references a closed path is materialized as a semantic
area region. The path is deterministically flattened, validated, converted once to polygon
primitives, and then consumed by the existing boolean visibility kernel.

### Runtime implementation

1. `runtime/visibility.py` gained deterministic closed-path flattening and `path_to_region()` for
   explicit semantic-region use. Cubic and quadratic curves are sampled deterministically; open
   paths are rejected for area use.
2. `runtime/region_maps.py` now materializes explicitly surfaced closed paths into polygon region
   contracts. Open nostril strokes remain non-area geometry. Path regions containing holes fail
   closed rather than silently dropping the holes.
3. `components/face/generators.py` adds explicit `depth_layer=0` to the head surface and
   `depth_layer=1` to the nose surfaces. These are authored ordering layers, not claimed physical
   3D distances.
4. `runtime/production_slice.py` adds `ProductionVisibilityResolution` and connects the exact
   camera-space geometry produced by the real render request to `resolve_visibility()` and
   `resolve_visibility_attribution()`.
5. The production overlap is strict: target owner is the HumanFace root/head surface, occluder is
   exactly the one Nose child, and the Nose must resolve to exactly one semantic area region.
6. `render/geometry_svg.py` consumes optional authored `depth_layer` metadata for path ordering;
   legacy ocular surfaces without the metadata retain their existing semantic paint priorities.
7. `runtime/visibility.py` hot-path geometry conversion was optimized after measurement: each front
   occluder planar region is materialized once per target region rather than once per arrangement
   cell.

### Evidence and visual QA

The actual production request generated front, +12° and -12° SVG/PNG samples. A diagnostic board
places each raw production image beside the exact semantic target/occluder geometry used by the
kernel. Diagnostic colors are QA-only and are not production appearance.

For all three samples:

- depth relation = `front`;
- target depth = 0;
- nose depth = 1;
- blocked head fraction = approximately 0.0122758892;
- visible head fraction = approximately 0.9877241108;
- nose area is fully inside the head area;
- raster IoU between kernel blocked area and exact nose semantic region = 1.0.

The board was manually inspected. The actual production image remains visually consistent: the
nose sits over the head, does not cover either eye, follows the ±12° placement rotation, and the
kernel diagnostic marks precisely the nose footprint.

### Performance evidence

The real production visibility resolution was measured before introducing any visibility cache.
The first V1.47 measurement had a median of 4,218,946.5 ns. After precomputing front occluder
regions once per target region, the median was 3,476,087.0 ns: approximately 17.61% lower on the
same workload. The warm production render median was 16,191,598.5 ns in the final benchmark.
No visibility cache was added because the measured workload does not yet justify a new lifetime or
cache-identity contract.

### Tests

The repository contains 111 test files and 956 collected tests at V1.47. Every test file was
executed to completion in 12 isolated batches of at most 10 files after monolithic/grouped runs
showed a historical process-state interaction in unrelated morphology tests. The release oracle is
therefore the isolated batch matrix, not the timed-out monolithic/grouped executions.

Final matrix: 955 passed, 1 expected PostgreSQL skip, 0 failed. The PostgreSQL test is skipped only
because `VISUAL_ENGINE_POSTGRES_DSN` is absent. Focused V1.45/V1.46/V1.47 production tests pass;
V1.24–V1.38 COLOR regression passes; the visibility kernel/attribution regression passes; and
`compileall -q src tests tools` passes.

### Files created

- `docs/runtime/production/V1.47_PRODUCTION_VISIBILITY_CONTRACT.md`
- `docs/runtime/production/V1.47_IMPLEMENTATION_REPORT_2026-09-30__part_01.md` (split document; see adjacent parts)
- `tests/unit/test_v147_production_visibility.py`
- `tools/audit_v147_production_visibility.py`
- `tools/benchmark_v147_visibility.py`
- `tools/visual_qa_v147_visibility.py`
- `tools/verify_v147_production_visibility.py`
- `artifacts/current/v1.47/*`

### Production files modified

- `src/visual_engine/runtime/visibility.py` — explicit closed-path area bridge + aggregate
  floating-point clamp + visibility hot-path region reuse.
- `src/visual_engine/runtime/region_maps.py` — explicit closed-surface path → semantic polygon
  materialization, fail-closed holes.
- `src/visual_engine/runtime/production_slice.py` — production overlap resolution result, exact
  head/nose extraction, depth relation, visibility and attribution calls.
- `src/visual_engine/components/face/generators.py` — authored head/nose depth layers.
- `src/visual_engine/render/geometry_svg.py` — optional explicit depth-layer paint ordering.
- `src/visual_engine/runtime/__init__.py` — exports `path_to_region` and
  `ProductionVisibilityResolution`.

No COLOR runtime file was modified. `effect_color.py`, `color_spaces.py` and `effects.py` remain
byte-identical to V1.46.

### Cleanup

The current V1.46 generated evidence directory was removed. Temporary test-matrix artifacts,
`__pycache__`, `.pyc`, temporary nose images and intermediate V1.47 matrix directories are removed
before release packaging. Historical V1.46 documentation remains available for traceability; its
current generated artifacts are not carried forward.
