<!-- Refactored from docs/governance/roadmap/ROADMAP__part_01.md; source lines 1602-1739; content preserved. -->
<!-- Part 13/16. Use the family index for navigation. -->
# V1.31 — Typed COLOR Consumer Migration — 2026-09-23

- [x] define the first typed COLOR-domain input as a minimal projection of the selected semantic role
- [x] make COLOR distinct from BASE even when both consume the same upstream role
- [x] define typed COLOR output vocabulary: canonical `ColorRGBA`, role, source and optional authored sRGB
- [x] preserve linear-sRGB RGBA and unassociated alpha without a resolver-time hex round trip
- [x] preserve role authority ID, source ID, lineage and bridge fingerprint
- [x] make `appearance_role_bridge` an explicit COLOR dependency identity
- [x] reject missing typed COLOR authority instead of silently falling back to legacy COLOR fields
- [x] reject a second legacy COLOR authority alongside the typed role
- [x] reject MATERIAL/LIGHTING data at the COLOR domain boundary
- [x] prove COLOR identity excludes geometry, transform, material, contour and unrelated siblings
- [x] implement targeted COLOR invalidation by delegating to the selected-role authority graph
- [x] cover authored BASE, inherited BASE, generated BASE and authored Palette paths
- [x] generate and manually inspect actual runtime COLOR visual evidence
- [x] add deterministic verifier and adversarial unit tests
- [x] bump engine/package version 1.3.6 → 1.3.7 and resolution identity 16 → 17
- [x] remove superseded V1.30 working artifact directory from the current checkpoint
- [ ] classify and migrate the next real legacy COLOR consumer; do not invent one merely to claim migration
- [ ] define any future color operation (mixing, saturation, temperature, pattern, grading) in a separate explicit contract before implementation

**V1.31 status:** `ENGINEERING PASS / TYPED COLOR PATH IMPLEMENTED / PROVENANCE + TARGETED INVALIDATION VERIFIED / VISUAL EVIDENCE INSPECTED / NO LIGHTING OR SHADING INTRODUCED`.

Evidence: `docs/domains/color/V1.31_TYPED_COLOR_CONSUMER_CONTRACT__part_01.md` (split document; see adjacent parts), `docs/domains/color/V1.31_IMPLEMENTATION_REPORT_2026-09-23__part_01.md` (split document; see adjacent parts), `tools/verify_v131_typed_color_consumer.py`, `artifacts/v131_typed_color_consumer/`.

# V1.32 — COLOR Consumer Audit — 2026-09-23

- [x] audit every production reference to `AppearanceDomain.COLOR`
- [x] audit `base_color`, `pattern`, `palette`, `contrast`, `saturation`, `vibrance`, `lightness`, and `temperature`
- [x] audit canonical color-space conversion entry points (`ColorRGBA` conversions and sRGB boundaries)
- [x] classify findings as canonical COLOR, legacy compatibility, color operation, palette, effect, supporting infrastructure, or non-COLOR domain
- [x] refuse to label code as dead without independent reachability evidence
- [x] identify production callers of `resolve_color_domain()` / `resolve_color_domain_from_typed()` outside the defining module
- [x] prove whether a real downstream COLOR migration target exists
- [x] migrate no consumer when the audit finds none; do not create a synthetic consumer merely to advance the version
- [x] run actual V1.31 runtime COLOR samples as diagnostic visual evidence
- [x] add deterministic audit tests and a dedicated gate
- [x] remove superseded V1.31 working artifact directory from the current checkpoint
- [x] keep engine/package and resolution versions unchanged because this brick changes audit/documentation tooling, not runtime semantics
- [ ] migrate the first genuinely existing downstream COLOR consumer when one is established
- [ ] if that consumer performs saturation/contrast/vibrance/temperature/mixing/pattern transformation, define input/output spaces, alpha, gamut, provenance, dependencies, invalidation and visual acceptance before implementing the operation

**V1.32 status:** `ENGINEERING PASS / PRODUCTION COLOR AUDIT PASS / ZERO DOWNSTREAM COLOR CONSUMERS / NO FABRICATED MIGRATION / VISUAL AUDIT EVIDENCE INSPECTED`.

Evidence: `docs/domains/color/V1.32_COLOR_CONSUMER_AUDIT_CONTRACT.md`, `docs/domains/color/V1.32_IMPLEMENTATION_REPORT_2026-09-23__part_01.md` (split document; see adjacent parts), `tools/audit_v132_color_consumers.py`, `tools/verify_v132_color_consumer_audit.py`, `artifacts/history/v1.32/color_consumer_audit/`.

# V1.33 — COLOR Downstream Closure Audit — 2026-09-24

- [x] build a conservative production symbol/call/import graph for the typed COLOR resolver boundary
- [x] identify both public COLOR resolver entry points and their incoming call edges
- [x] distinguish the internal `resolve_color_domain_from_typed()` wrapper from a real downstream caller
- [x] inspect dynamic-dispatch escape hatches (`getattr`, resolver-name strings, local resolver aliases and import indirection)
- [x] fail closed on unresolved dynamic dispatch instead of guessing reachability
- [x] prove the current resolver boundary has zero downstream production callers and zero dynamic escape hatches
- [x] run actual V1.31 COLOR resolver samples through the unchanged runtime for visual evidence
- [x] add deterministic V1.33 gate and adversarial tests
- [x] keep ENGINE_VERSION / RESOLUTION_VERSION unchanged because no runtime semantics changed
- [x] remove the superseded V1.32 working artifact directory from the current checkpoint
- [ ] implement a COLOR operation only after a real downstream production caller exists
- [ ] if a caller transforms color, freeze input/output spaces, alpha, gamut, provenance, dependency, invalidation, cache and visual acceptance before algorithm implementation

**V1.33 status:** `ENGINEERING PASS / DOWNSTREAM CLOSURE AUDIT PASS / ZERO PRODUCTION COLOR CALLERS / ZERO DYNAMIC ESCAPE HATCHES / NO RUNTIME COLOR ALGORITHM ADDED / VISUAL EVIDENCE INSPECTED`.

Evidence: `docs/domains/color/V1.33_COLOR_DOWNSTREAM_CLOSURE_CONTRACT.md`, `docs/domains/color/V1.33_IMPLEMENTATION_REPORT_2026-09-24__part_01.md` (split document; see adjacent parts), `tools/audit_v133_color_downstream_closure.py`, `tools/verify_v133_color_downstream_closure.py`, `artifacts/history/v1.33/color_downstream_closure/`.


# V1.34 — First Real Downstream COLOR Operation — 2026-09-24

- [x] trace an actually reachable production color transformation instead of the typed COLOR resolver only
- [x] prove the production path `resolve_component → resolve_effects → apply_effect_color`
- [x] explicitly distinguish this effect consumer from the still-closed typed COLOR resolver boundary
- [x] define input representation as canonical linear-sRGB `ColorRGBA`
- [x] define calculation space as encoded sRGB 8-bit interpolation to preserve established visual semantics
- [x] define output representation as canonical linear-sRGB `ColorRGBA`
- [x] define effect alpha as the sole RGB-effect strength; preserve target/base alpha
- [x] define behavior for neutral, extreme, dark, light, saturated and alpha-bearing colors
- [x] define fail-closed gamut behavior through `ColorRGBA` construction with no gamut mapping
- [x] preserve operation identity/version, lineage and effect fingerprints in the color operation result
- [x] preserve resolution-level dependency/invalidation behavior and bump resolution identity because runtime semantics changed
- [x] migrate `resolve_effects` so internal color transforms no longer use the legacy string helper
- [x] retain `apply_shadow_color` only as an explicit legacy compatibility adapter
- [x] optimize non-color effect paths by materializing canonical colors lazily
- [x] decode each effect color once per shadow/tint operation and reuse it for fill/contour
- [x] verify RGB output against the established pre-V1.34 law over a broad channel sample
- [x] verify base-alpha preservation
- [x] generate and manually inspect actual runtime visual evidence
- [x] add deterministic audit, gate and adversarial tests
- [x] update engine/package version to 1.3.8 and resolution identity to 18
- [x] remove superseded V1.33 current artifact directory from the final checkpoint after evidence capture
- [ ] implement another COLOR transformation only when a distinct real production consumer is identified

**V1.34 status:** `ENGINEERING PASS / REAL SHADOW-TINT CONSUMER PROVEN / CANONICAL COLOR BOUNDARY / LEGACY RGB VISUAL LAW PRESERVED / BASE ALPHA PRESERVED / VISUAL EVIDENCE INSPECTED`.

Evidence: `docs/domains/color/V1.34_FIRST_REAL_COLOR_CONSUMER_CONTRACT__part_01.md` (split document; see adjacent parts), `docs/domains/color/V1.34_IMPLEMENTATION_REPORT_2026-09-24__part_01.md` (split document; see adjacent parts), `tools/audit_v134_first_real_color_consumer.py`, `tools/verify_v134_first_real_color_consumer.py`, `tools/visual_qa_v134_first_real_color_consumer.py`, `artifacts/v134_first_real_color_consumer/`.


# V1.36 — COLOR Downstream Audit — 2026-09-24

- [x] enumerate every production direct `ColorRGBA` consumer outside `runtime/color_spaces.py` and `runtime/effect_color.py`
- [x] trace each use to its actual owner: authority, palette, persistence, validation, compatibility or already-closed effect path
- [x] classify representation conversions separately from true color transformations
- [x] audit HSL, OKLab, XYZ and sRGB operations outside the canonical color-space boundary
- [x] audit renderer-local RGBA arithmetic separately from generic COLOR semantics
- [x] audit eye-specific color and reference RGB analysis separately; keep eye style out of generic COLOR runtime
- [x] prove zero distinct new generic COLOR transformations
- [x] generate actual runtime samples for BASE, Palette, renderer RGBA and eye SVG paths
- [x] add deterministic V1.36 audit/gate tests
- [x] verify byte-for-byte unchanged production runtime Python against the V1.35 certified checkpoint
- [x] keep engine/package/resolution versions unchanged because no runtime semantic algorithm changed
- [x] remove superseded V1.35 current artifact directory after evidence capture
- [ ] implement one new COLOR operation only if a distinct real production transformation is later proven
- [ ] before any such implementation, freeze input/calculation/output spaces, alpha, bounds, neutral/extreme behavior, gamut, provenance, lineage, dependencies, invalidation, cache, determinism, performance and visual acceptance

**V1.36 status:** `ENGINEERING PASS / NON-EFFECT COLOR SURFACE AUDITED / ZERO NEW GENERIC COLOR TRANSFORMATIONS / EYE COLOR ISOLATED / RENDERER RGBA SEPARATED / RUNTIME UNCHANGED / VISUAL EVIDENCE INSPECTED`.

Evidence: `docs/domains/color/V1.36_COLOR_DOWNSTREAM_CONTRACT.md`, `docs/domains/color/V1.36_IMPLEMENTATION_REPORT_2026-09-24__part_01.md` (split document; see adjacent parts), `tools/audit_v136_color_downstream.py`, `tools/verify_v136_color_downstream.py`, `tools/visual_qa_v136_color_downstream.py`, `artifacts/history/v1.36/color_downstream/`.


# V1.35 — VisualEffect COLOR Surface Audit — 2026-09-24

- [x] enumerate every production `VisualEffect.kind` and classify `shadow`, `tint`, `opacity`, `visibility`, and `occlusion` by actual runtime behavior
- [x] trace effect creation through direct resolution context, legacy shadow injection, relation metadata and consequence bindings
- [x] prove `shadow` and `tint` share exactly one existing canonical `effect.color.srgb8-interpolation` operation
- [x] distinguish scalar opacity/visibility/occlusion from RGB color operations
- [x] search for direct encoded-RGB arithmetic outside the explicit canonical effect/color-space boundary
- [x] fail closed on unresolved dynamic `VisualEffect.kind` construction; validated relation/consequence passthroughs remain explicitly classified
- [x] prove the legacy `runtime/contract.py::_apply_shadow` helper had zero repository call sites before removing it
- [x] remove the proven-dead helper and verify zero remaining direct RGB arithmetic outside the canonical boundary
- [x] generate actual `resolve_component()` visual samples for shadow, tint, opacity, visibility and occlusion and inspect them
- [x] add deterministic audit, gate and adversarial tests
- [x] keep engine/package/resolution versions unchanged because no runtime semantic algorithm changed
- [x] remove superseded V1.34 current artifact directory after evidence capture
- [ ] implement another COLOR operation only if V1.35 or a future audit identifies a distinct real production transformation

**V1.35 status:** `ENGINEERING PASS / EFFECT COLOR SURFACE AUDITED / ONE DISTINCT COLOR OPERATION / SCALAR EFFECTS SEPARATED / DEAD HELPER REMOVED AFTER PROOF / NO NEW COLOR ALGORITHM WARRANTED / VISUAL EVIDENCE INSPECTED`.

Evidence: `docs/domains/color/V1.35_EFFECT_COLOR_SURFACE_CONTRACT.md`, `docs/domains/color/V1.35_IMPLEMENTATION_REPORT_2026-09-24__part_01.md` (split document; see adjacent parts), `tools/audit_v135_effect_color_surface.py`, `tools/verify_v135_effect_color_surface.py`, `tools/visual_qa_v135_effect_color_surface.py`, `artifacts/v135_effect_color_surface/`.
