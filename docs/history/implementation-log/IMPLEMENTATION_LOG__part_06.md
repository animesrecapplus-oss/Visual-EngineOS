<!-- Refactored from ['docs/history/implementation-log/IMPLEMENTATION_LOG__part_01.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_02.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_03.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_04.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_05.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_06.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_07.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_08.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_09.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_10.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_11.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_12.md']; source lines 698-842; content preserved. -->
<!-- Part 6/12. Use the family index for navigation. -->
## Explicit nonclaims

- LIVE_POSTGRES = UNVERIFIED
- PACKAGE_BUILD = NOT VERIFIED unless a build is actually executed successfully
- PRODUCTION_ART_QUALITY = NOT CLAIMED
- no color mixing, grading, lighting, shading, BRDF, material response, transmission, reflection or
  renderer post-processing was implemented
- no legacy COLOR consumer was invented or falsely declared migrated

## Next V1.32 micro-scope

The next brick must begin with a source audit of the repository's **actual** remaining COLOR consumers.
For each caller, classify whether it needs the typed canonical color, a legacy compatibility field, a
style operation, a palette operation, or a separate effect. Migrate only a genuinely existing caller.
If an operation changes the color value (mixing, saturation, contrast, temperature, vibrance, pattern),
define its value space, authority, provenance, dependency fingerprint and fail-closed semantics before
implementing it. Add visual evidence for the actual semantic effect and reject any implementation whose
artifact is numerically consistent but visually inconsistent with the declared operation. Do not pull in
lighting/material/shading merely to make the result visually richer.


## V1.32 — COLOR Consumer Audit — 2026-09-23

### Objective

Audit the real production tree before claiming another COLOR consumer migration. The audit had to distinguish typed COLOR infrastructure from legacy compatibility, Palette, color-space operations, EFFECT-domain color operations and unrelated color-looking fields.

### Implementation

1. Added `tools/audit_v132_color_consumers.py`, using Python AST traversal rather than grep-only matching.
2. Scanned all 170 production Python files for `AppearanceDomain.COLOR`, the requested legacy vocabulary (`base_color`, `pattern`, `palette`, `contrast`, `saturation`, `vibrance`, `lightness`, `temperature`), COLOR resolver calls and canonical color-space conversion entry points.
3. Classified every recorded finding into an explicit category and left no finding unclassified.
4. Defined a true downstream COLOR consumer as production code outside `runtime/color_resolution.py` that actually invokes the typed COLOR resolver and consumes its result.
5. Confirmed there are zero such callers in the current production tree.
6. Deliberately did not migrate `runtime/effects.py`, Palette infrastructure, persistence or renderer eye-color fields because those belong to other domains/authorities and are not consumers of the typed COLOR-domain result.
7. Refused to claim dead code where independent reachability evidence is absent.
8. Added `tools/verify_v132_color_consumer_audit.py` and `tests/unit/test_v132_color_consumer_audit.py`.
9. Added `tools/visual_qa_v132_color_consumer_audit.py`; its swatches are generated from actual V1.31 resolver outputs and encoded with `ColorRGBA.to_rgba8()` only for display.
10. Removed the superseded `artifacts/v131_typed_color_consumer/` directory from the current checkpoint while retaining historical V1.31 documentation.

### Result

- 170 production Python files audited.
- 206 relevant findings recorded.
- 0 downstream production COLOR consumers.
- 0 unclassified findings.
- 0 unproven dead-code claims.
- Migration target: none warranted.
- Runtime version policy unchanged (`ENGINE_VERSION=1.3.7`, `RESOLUTION_VERSION=17`) because no runtime semantics changed.

### Evidence

`artifacts/history/v1.32/color_consumer_audit/V1.32_COLOR_CONSUMER_AUDIT.json`
`artifacts/history/v1.32/color_consumer_audit/V1.32_COLOR_CONSUMER_AUDIT_RUNTIME_BOARD.png`
`tools/verify_v132_color_consumer_audit.py`
`tests/unit/test_v132_color_consumer_audit.py`

### Next micro-scope

The next runtime migration remains conditional: identify the first genuine downstream consumer of the typed COLOR result. If it performs an actual transformation, first freeze the mathematical contract (input/output spaces, alpha semantics, gamut policy, provenance, dependencies, invalidation, determinism, bounds and visual acceptance), then implement only that operation and its smallest real consumer.


## V1.33 — COLOR Downstream Closure Audit — 2026-09-24

### Objective

Close the V1.32 audit one level deeper: prove whether the typed COLOR resolver result has a real production downstream path. The audit must not confuse public exports, the internal typed wrapper, unrelated color operations or legacy vocabulary with an actual consumer.

### Implementation

1. Added `tools/audit_v133_color_downstream_closure.py`, which parses all production Python files, collects 1140 symbols and 1464 direct call edges, resolves import aliases and module-qualified calls, and inspects common dynamic-dispatch escape hatches.
2. Corrected the graph module-name construction during self-review so `visual_engine` is not duplicated in qualified symbols.
3. Corrected `__all__` handling so public string exports are not falsely classified as dynamic resolver dispatch.
4. Kept unresolved dynamic dispatch fail-closed: a non-export resolver string, alias or dynamic attribute would block the closure PASS rather than being guessed.
5. Confirmed the sole incoming resolver edge is `resolve_color_domain_from_typed()` → `resolve_color_domain()` inside `runtime/color_resolution.py`.
6. Confirmed zero downstream production COLOR callers and zero dynamic resolver escape hatches.
7. Added `tools/verify_v133_color_downstream_closure.py` and four focused tests in `tests/unit/test_v133_color_downstream_closure.py`.
8. Added `tools/visual_qa_v133_color_downstream_closure.py`; its two swatches are direct outputs from the unchanged V1.31 COLOR resolver.
9. No runtime source file, version constant, resolver algorithm or migration target was changed.
10. Removed the superseded `artifacts/history/v1.32/color_consumer_audit/` directory from the current checkpoint while retaining V1.32 documentation as historical provenance.

### Result

- 170 production Python files parsed.
- 1140 production symbols collected.
- 1464 direct call edges collected.
- 1 incoming edge to the COLOR resolver, and it is internal to `runtime/color_resolution.py`.
- 0 downstream production COLOR callers.
- 0 dynamic resolver escape hatches.
- 0 runtime semantic changes.
- migration target: none warranted.

### Evidence

`artifacts/history/v1.33/color_downstream_closure/V1.33_COLOR_DOWNSTREAM_CLOSURE_AUDIT.json`
`artifacts/history/v1.33/color_downstream_closure/V1.33_COLOR_DOWNSTREAM_CLOSURE_RUNTIME_BOARD.png`
`tools/verify_v133_color_downstream_closure.py`
`tests/unit/test_v133_color_downstream_closure.py`

### Next micro-scope

Do not implement a color transform until a real production caller consumes the typed COLOR result. If such a caller is established, trace its exact data use first. If it transforms color, freeze input/calculation/output spaces, channel bounds, neutral/extreme behavior, alpha participation, gamut policy, provenance, lineage, dependency fingerprint, invalidation, cache identity, determinism, performance and visual acceptance before writing the operation.


## V1.34 — First Real Downstream COLOR Operation — 2026-09-24

V1.34 followed the V1.33 closure audit rather than inventing a typed-COLOR resolver caller. A real existing production path was traced: `runtime/contract.py::resolve_component` calls `runtime/effects.py::resolve_effects`, whose shadow/tint branch transformed encoded hex RGB directly.

The transformation was moved behind `runtime/effect_color.py::apply_effect_color`. Canonical `ColorRGBA` is now used at the operation boundaries. The established encoded-sRGB 8-bit interpolation law is retained deliberately for visual continuity; the result is reconstructed as canonical linear-sRGB RGBA. Base alpha is preserved and effect-color alpha remains non-authoritative.

The internal legacy string helper `apply_shadow_color` remains only as an explicit compatibility adapter. `resolve_effects` uses the canonical path. Non-color effects avoid unnecessary color conversion, and each shadow/tint effect color is decoded once and shared between fill and contour.

Evidence includes broad regression tests against the old RGB law, alpha-preservation tests, provenance assertions, sibling-isolation tests, a static reachability audit, a runtime visual board, version-policy updates and A4–A10 release verification.


## V1.35 — VisualEffect COLOR Surface Audit — 2026-09-24

### Objective

Audit the remaining generic `VisualEffect` color surface after V1.34, distinguish real RGB transformations from scalar visibility/opacity effects, trace all effect creation paths, close direct-RGB arithmetic outside the canonical boundary, and avoid inventing a second COLOR algorithm.

### Implementation

1. Added `tools/audit_v135_effect_color_surface.py` to parse all production Python files and classify the five effect kinds by actual runtime behavior.
2. Traced direct effect construction, relation metadata effects, consequence-bound effects and the legacy `ResolutionContext.shadow_alpha` compatibility injection.
3. Proved `shadow` and `tint` both converge on the single `effect.color.srgb8-interpolation` operation.
4. Classified `opacity`, `visibility` and `occlusion` as scalar effects; they do not modify RGB.
5. Searched for direct encoded-RGB arithmetic outside the canonical `runtime/effect_color.py` / `runtime/color_spaces.py` boundary.
6. Before cleanup, proved `runtime/contract.py::_apply_shadow` had zero repository call sites and was not exported; captured the proof in `V1.35_DEAD_HELPER_PRE_CLEANUP_EVIDENCE.json`.
7. Removed the unreferenced helper; the post-cleanup audit reports zero direct RGB arithmetic outside the canonical boundary.
8. Added `tools/verify_v135_effect_color_surface.py`, eight focused unit tests and a runtime visual board.
9. Kept engine/package/resolution versions unchanged because no runtime algorithm changed.
10. Removed the superseded V1.34 current artifact directory before final packaging while retaining historical V1.34 documentation.

### Result

- 171 production Python files audited.
- 5 `VisualEffect` kinds classified.
- 3 dynamic effect-kind construction sites identified as validated consequence/relation passthroughs; no unresolved dynamic kind was accepted.
- 2 canonical `apply_effect_color` call sites: the compatibility adapter and the internal resolver path.
- 1 distinct COLOR operation: `effect.color.srgb8-interpolation`.
- 0 direct RGB arithmetic findings outside the canonical boundary after cleanup.
- 1 legacy helper removed after repository-wide zero-call proof.
- 0 new COLOR algorithms invented.
