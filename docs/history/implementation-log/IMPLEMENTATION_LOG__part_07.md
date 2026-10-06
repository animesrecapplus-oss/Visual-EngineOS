<!-- Refactored from ['docs/history/implementation-log/IMPLEMENTATION_LOG__part_01.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_02.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_03.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_04.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_05.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_06.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_07.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_08.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_09.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_10.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_11.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_12.md']; source lines 843-963; content preserved. -->
<!-- Part 7/12. Use the family index for navigation. -->
### Test evidence

The checkpoint collection contains 849 tests across 99 test files. Composite fresh-process evidence records 848 passed, 1 skipped and 0 failed; the monolithic run was attempted but did not complete within the checkpoint execution window, so no monolithic PASS is claimed. The V1.35 focused suite and V1.34 effect regression suite passed independently.

### Visual evidence

`artifacts/v135_effect_color_surface/V1.35_EFFECT_COLOR_SURFACE_RUNTIME_BOARD.png` contains actual `resolve_component()` outputs for shadow, tint, opacity, visibility and occlusion. Shadow/tint visibly alter RGB; scalar effects leave RGB unchanged while changing only their scalar outputs.

### Next micro-scope

Do not create another COLOR operation unless a distinct real production transformation is found. The next audit should inspect the remaining non-effect color-bearing surfaces only where an actual downstream transformation exists; if no such operation is found, preserve the current one-operation boundary rather than expanding the architecture speculatively.

## V1.36 — COLOR Downstream Audit — 2026-09-24

### Objective

Audit every real production consumer of canonical `ColorRGBA` outside `runtime/color_spaces.py`
and `runtime/effect_color.py`; trace each use to its actual owner; separate serialization,
compatibility, representation conversion, palette, rendering and genuine color transformation;
audit eye-specific color separately; and refuse to invent a new COLOR algorithm if no distinct
production transformation exists.

### Implementation

1. Added `tools/audit_v136_color_downstream.py` with AST-aware symbol/enclosing-function tracing,
   color-space operation detection, renderer/eye RGB arithmetic classification and explicit
   consumer ownership classification.
2. Added `tools/verify_v136_color_downstream.py` as a fail-closed gate. It verifies zero new
   generic transformations, zero HSL/OKLab/XYZ operations outside the canonical boundary, zero
   eye `ColorRGBA` dependency and byte-for-byte runtime-source equality against the V1.35 ZIP.
3. Added `tests/unit/test_v136_color_downstream.py` covering the audit conclusion, consumer
   classification, BASE and Palette runtime hand-off, renderer separation and runtime immutability.
4. Added `tools/visual_qa_v136_color_downstream.py`. It samples actual typed COLOR BASE/Palette
   resolution, renderer-local RGBA compositing and a real eye SVG/raster output.
5. Added the V1.36 contract and implementation report.
6. Updated A4/A10 synchronization tools to recognize V1.36 as the current checkpoint.
7. Updated CURRENT_STATUS, ROADMAP, ENGINE_VISION and this implementation log; added decision D-083.
8. No production runtime Python source was modified.

### Result

- 171 production Python files audited.
- 6 direct `ColorRGBA` consumer files found outside the two canonical color modules; 5 are
  non-effect authority/compatibility/persistence/validation surfaces and the sixth is the already
  closed effect path.
- 0 HSL/OKLab/XYZ operations outside the canonical color-space module.
- 0 generic `ColorRGBA` imports in the eye production domain.
- 3 renderer-local RGBA arithmetic findings, all owned by `render/canvas.py`.
- 0 new generic COLOR transformations.
- 0 runtime source files changed relative to V1.35.
- engine/package/resolution versions unchanged at 1.3.8 / 18.

### Test / visual evidence

The focused V1.36 + prior color/effect regression suite collected 162 tests and passed 162/162.
The checkpoint-wide composite evidence records 856 collected tests, 855 passed, 1 skipped and 0 failed. The 99 pre-existing test files were byte-identical to V1.35 and their prior 849 outcomes were reused after byte-identity verification; the new V1.36 test file ran fresh with 7/7 passes. No monolithic full-suite PASS is claimed.
The V1.36 gate passed. The runtime board and eye SVG/raster sample were generated from actual
runtime execution and visually inspected. No production-art quality or full renderer color-
management certification is claimed.

### V1.36 release-evidence correction — 2026-09-25

Independent replay of the packaged checkpoint found that the first verifier depended on a
temporary V1.35 ZIP path. Runtime source was already byte-identical, but the evidence was not
portable. The fix captures the 171-file V1.35 production-runtime SHA-256 fingerprint in
`artifacts/history/v1.36/color_downstream/V1.35_RUNTIME_BASELINE_SHA256.json` and makes the verifier
consume that packaged evidence. The superseded V1.35 artifact directory remains absent.
The V1.35 effect regression test was made independent of that deleted directory.

Files changed in this correction:
- `tools/verify_v136_color_downstream.py`
- `tests/unit/test_v135_effect_color_surface.py`
- `docs/domains/color/V1.36_COLOR_DOWNSTREAM_CONTRACT.md`
- `docs/domains/color/V1.36_IMPLEMENTATION_REPORT_2026-09-24__part_01.md` (split document; see adjacent parts)
- `docs/history/implementation-log/IMPLEMENTATION_LOG__part_01.md` (split document; see adjacent parts)
- `artifacts/history/v1.36/color_downstream/V1.35_RUNTIME_BASELINE_SHA256.json`

No `src/visual_engine` runtime file changed.

### Next micro-scope

V1.37 is a discovery gate for one concrete real production color transformation. If none exists,
keep runtime unchanged. If exactly one exists, freeze its complete input/calculation/output/alpha/
bounds/gamut/provenance/dependency/invalidation/cache/determinism/performance/visual contract,
then implement one operation only and validate it with runtime samples before packaging.

## V1.37 — 2026-09-25 — COLOR consumer audit

- Re-opened the V1.36 downstream COLOR consumer graph from the corrected certified checkpoint.
- Compared all 171 production Python files against the V1.36 immutable source fingerprint: 0 added, 0 removed, 0 changed.
- Identified the single real color-modifying consumer as `runtime/effects.py` delegating to the existing `runtime/effect_color.py` operation `effect.color.srgb8-interpolation`.
- Classified it as a **pre-existing true transformation**, not a new V1.37 transformation.
- Re-audited input/output space, representation, alpha, bounds, neutral/extreme behavior, gamut, provenance, lineage, fingerprint, invalidation, cache, determinism, performance and visual criteria.
- Added runtime-backed V1.37 adversarial tests and generated/visually inspected real effect samples.
- Deliberately made no `src/visual_engine` runtime change; adding a second operation would have been unsupported by the evidence.
- Created: `tools/audit_v137_color_consumer.py`, `tools/visual_qa_v137_color_consumer.py`, `tests/unit/test_v137_color_consumer.py`, V1.37 audit/evidence/sample artifacts, and V1.37 contract/report documentation.

## V1.38 — 2026-09-25 — EFFECT COLOR semantic closure

- Re-opened the complete `effect_color` call path and enumerated every production call to `apply_effect_color()` and `_apply_canonical_effect()` with AST evidence.
- Confirmed exactly two production `apply_effect_color()` call sites: the legacy `apply_shadow_color()` adapter and `_apply_canonical_effect()`.
- Confirmed exactly two production `_apply_canonical_effect()` call sites: fill and contour.
- Proved that production RGB-effect alpha authority remains singular: `VisualEffect.alpha → effect_alpha`.
- Audited production code for implicit `effect.color.alpha` use: zero findings.
- Tested fill/contour lineage and corrected the previous single-step lineage behavior so successive color effects carry the complete ordered `(source_id, effect_id)` history.
- Audited `shadow→shadow`, `tint→tint`, `shadow→tint` and `tint→shadow` chains through the real resolver.
- Audited effect priority and deterministic equal-priority ordering `(priority, effect_id, source_id)`.
- Verified duplicate effect IDs fail closed before color application.
- Found and corrected a fingerprint dependency weakness: an external effect fingerprint can no longer mask a changed actual effect color.
- Added explicit ordered-lineage fingerprinting and shared effect fingerprints between fill/contour to avoid duplicate dependency hashing.
- Reused the existing `effect.color.srgb8-interpolation` operation without introducing a new color space or transformation.
- Audited the inside of `effect_color.py` and found no second HSL/OKLab/XYZ/gamut/compositing/color operation.
- Measured real resolver cost for 0/1/2/4/8 color effects and retained the exact local measurements as JSON/CSV evidence.
- Generated a real `resolve_effects()` multi-effect visual board covering dark, mid, highlight, close, complementary and alpha-bearing colors; inspected the PNG manually.
- Bumped only `RESOLUTION_VERSION` from 18 to 19 because fingerprint/lineage invalidation semantics changed; `ENGINE_VERSION` and `SCHEMA_VERSION` remain unchanged.
- Removed superseded `artifacts/v137_color_consumer/` from the current checkpoint and decoupled its regression test from that generated directory.
- Added: `docs/domains/color/V1.38_EFFECT_COLOR_SEMANTIC_CLOSURE_CONTRACT__part_01.md` (split document; see adjacent parts), `docs/domains/color/V1.38_IMPLEMENTATION_REPORT_2026-09-25__part_01.md` (split document; see adjacent parts), `tools/audit_v138_effect_color_closure.py`, `tools/verify_v138_effect_color_closure.py`, `tools/benchmark_v138_effect_color.py`, `tools/visual_qa_v138_effect_color_closure.py`, `tests/unit/test_v138_effect_color_closure.py`, and `artifacts/v138_effect_color_closure/`.
- Modified: `src/visual_engine/runtime/effect_color.py`, `src/visual_engine/runtime/effects.py`, `src/visual_engine/runtime/version_policy.py`, `tests/unit/test_v137_color_consumer.py`, `tests/unit/test_v133_color_downstream_closure.py`, plus the current documentation/history files.

**V1.38 result:** `ENGINEERING PASS / EFFECT COLOR SEMANTIC CLOSURE PASS / NO SECOND COLOR TRANSFORMATION / ALPHA AUTHORITY CLOSED / MULTI-EFFECT LINEAGE CLOSED / FINGERPRINT INVALIDATION CLOSED / VISUAL EVIDENCE INSPECTED`.
