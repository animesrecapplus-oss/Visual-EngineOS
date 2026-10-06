<!-- Refactored from ['docs/history/implementation-log/IMPLEMENTATION_LOG__part_01.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_02.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_03.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_04.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_05.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_06.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_07.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_08.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_09.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_10.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_11.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_12.md']; source lines 1519-1541; content preserved. -->
<!-- Part 12/12. Use the family index for navigation. -->
### Next micro-scope — V1.48

V1.48 must not add another face family yet. The next step is to turn the proven head←nose overlap
from a single production pair into a more general **multi-component production visibility envelope**
only after proving that the current explicit contract generalizes without semantic shortcuts.

Required micro-steps:

1. freeze the V1.47 head←nose semantic-region/depth contract as a regression fixture;
2. identify whether a second real occluding relation already exists in production geometry, rather
   than manufacturing one;
3. if and only if such a pair exists, connect it through the same request-owned visibility boundary;
4. verify multiple occluders with overlap, exclusive coverage, shared coverage and dominant depth;
5. compare multi-occluder attribution against actual rendered layer order;
6. test coplanar and behind relations explicitly;
7. test opacity/transmission only if an actual production material uses them;
8. measure visibility cost with 1, 2 and N real occluders before considering a cache or spatial index;
9. evaluate whether semantic-region fingerprints need explicit invalidation identity;
10. repeat concurrent sessions, injected-cache ownership, stale graph, teardown, deterministic SVG,
    visual regression and COLOR gates;
11. do not add mouth/ear/hair geometry merely to create an occluder;
12. do not introduce a physical 3D/z-buffer claim until the current 2D semantic-depth contract is
    demonstrably insufficient for an actual production requirement.

### V1.48 completion — source-code modularization audit — 2026-09-30

#### Audit performed

- audited 174 production Python modules;
- counted 67 modules above 150 lines;
- built 408 direct internal import edges in the V1.47 baseline;
- found three pre-existing runtime SCCs and verified the new module participates in none;
- found no exact duplicate function-body group;
- manually rejected one 97.9% similarity candidate as a domain-contract false positive.

#### Selected extraction

The chosen seam was `src/visual_engine/runtime/visibility.py`: planar-region materialization was
mixed with boolean visibility/depth/optical event resolution. The materialization responsibility was
moved to `src/visual_engine/runtime/region_geometry.py`.

#### Files created

- `src/visual_engine/runtime/region_geometry.py` — 150 lines at source freeze.
- `tests/unit/test_v148_source_modularization.py` — ownership/API/determinism/contract tests.
- `tools/audit_v148_source_modularization.py` — repeatable structural audit.
- `tools/benchmark_v148_source_modularization.py` — repeatable runtime benchmark.
- `docs/refactor/V1.48_SOURCE_MODULARIZATION_CONTRACT.md`.
- `docs/refactor/V1.48_SOURCE_MODULARIZATION_REPORT.md`.
- `docs/refactor/ARTIFACT_RETENTION_POLICY.md`.

#### Files modified

- `src/visual_engine/runtime/visibility.py` — region helpers removed; compatibility imports retained.
- `src/visual_engine/runtime/region_maps.py` — direct region-owner import.
- `src/visual_engine/runtime/placement.py` — direct region-owner import.
- `src/visual_engine/runtime/placement_constraints.py` — direct region-owner import.
- `src/visual_engine/runtime/visibility_attribution.py` — direct region-owner import.
- `src/visual_engine/runtime/__init__.py` — public exports assigned to the new owner.
- governance/status/roadmap/decision indexes — V1.48 status and V1.49 next scope.
- README and refactor indexes — artifact retention and modularization policy.

#### Line ranges at final freeze

Exact ranges are recorded after the final source freeze in the V1.48 report. The source extraction was
kept intentionally narrow: one module, one responsibility, one regression boundary.

#### Validation

Focused visibility/modularization tests passed before the complete regression. Fresh-process benchmarks
showed +1.14% median region-conversion cost and -4.83% median warm production-render cost relative to
the V1.47 source baseline; no optimization outside the extraction was introduced.

Final source line map: `region_geometry.py` 1–150; `visibility.py` original region blocks 31–66 and 132–274
removed; `visibility.py` final 291 lines; `runtime/__init__.py` export split 62–71; `region_maps.py`
11; `placement.py` 20; `placement_constraints.py` 19; `visibility_attribution.py` 31–32; modularization
tests 1–90; audit tool 1–132; benchmark tool 1–50; test-matrix report output made opt-in at
`run_full_test_matrix.py` lines 22–23 and 88–109; historical COLOR audits now return in-memory reports.

Full regression: 112 test files / 962 collected / 961 passed / 1 expected PostgreSQL skip / 0 failed.
The real production SVG before/after refactor is byte-identical (15,168 bytes; SHA-256
`7bce6ee07c056452b3c3544beb794c3011a9dc56d9a15c01d21ca75ba4b11696`).
All generated V1.47 current/history/release artifacts were removed. The certified V1.48 ZIP is the only
retained generated release artifact and is delivered outside the project tree.

### V1.49 completion — GeometryContract transformation extraction — 2026-09-30

#### Audit and selection

The V1.48 tree was re-audited before code movement: 175 modules, 411 direct internal import edges,
67 modules above 150 lines, three known SCCs and zero exact duplicate function-body groups. The chosen
module was `runtime.geometry_transform` because its transform-context resolution and concrete
GeometryContract transformation were independently identifiable responsibilities with real consumers.

#### Created

- `src/visual_engine/runtime/geometry_contract_transform.py`;
- `tests/unit/test_v149_source_modularization.py`;
- `tools/audit_v149_source_modularization.py`;
- `tools/benchmark_v149_source_modularization.py`;
- `docs/refactor/V1.49_SOURCE_MODULARIZATION_CONTRACT.md`;
- `docs/refactor/V1.49_SOURCE_MODULARIZATION_REPORT.md`.

#### Modified

- `src/visual_engine/runtime/geometry_transform.py`;
- `src/visual_engine/runtime/placement.py`;
- `src/visual_engine/runtime/placement_visibility.py`;
- `src/visual_engine/runtime/__init__.py`;
- artifact-retention policy and V1.48 report clarification;
- governance decision/status/roadmap and this history record.

#### Final source map

`geometry_contract_transform.py` owns lines 1–173. `geometry_transform.py` retains context resolution
and imports the owner at lines 18–19; `resolve_geometry_contract` is lines 139–161. Direct owner imports
are `placement_visibility.py` line 17 and `placement.py` line 351; public ownership is assigned in
`runtime/__init__.py` lines 36–50. V1.49 tests are lines 1–62; audit tool lines 1–168; benchmark tool
lines 1–60. Artifact-policy tests are updated at `test_v13_a5_visual_qa.py` lines 13–26 and
`test_v144_production_vertical_slice.py` lines 8–18.

#### Validation

Focused V1.49/modularization/geometry/production tests: 52 passed. Complete deterministic matrix: 113 test files / 967 collected / 966 passed / 1 expected PostgreSQL skip /
0 failed. Fresh-process five-run median-of-medians: extracted transform 17,697 ns → 17,638 ns (-0.33%); warm production render 22,513,568 ns →
22,019,193.5 ns (-2.20%). V1.48 and V1.49 production SVGs are byte-identical, 15,168 bytes,
SHA-256 `7bce6ee07c056452b3c3544beb794c3011a9dc56d9a15c01d21ca75ba4b11696`.

The artifact policy was corrected: `artifacts/` is retained, while superseded generated contents are
purged. Only the current V1.49 visual evidence remains under `artifacts/current/v1.49/`.

### V1.50 next micro-scope

Repeat the dependency graph, responsibility inventory, consumer trace and duplicate audit from the V1.49
tree; select one module and one independent responsibility; extract one owner; test API/cycles/adversarial
invariants; run the full matrix; benchmark against V1.49; visually compare only if output can change;
keep COLOR frozen; purge superseded generated evidence while retaining `artifacts/`; update exact line
records; and deliver one certified ZIP. No extraction is justified solely by the 150-line threshold.
