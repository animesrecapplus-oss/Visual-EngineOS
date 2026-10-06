<!-- Refactored from docs/governance/status/CURRENT_STATUS__part_01.md; source lines 1-138; content preserved. -->
<!-- Part 1/4. Use the family index for navigation. -->
# Visual Engine — Current Authoritative Status

**Current checkpoint:** V1.44 Production Vertical-Slice Audit
**Baseline:** V1.23 architectural realignment checkpoint
**Date:** 2026-09-29

This file is the current status surface. Older V1.3/A0–A10 status blocks remain historical
provenance and must not be interpreted as the current frontier.

## Current state

- **V1.24 canonical color spaces:** implemented; internal appearance color is linear-sRGB RGBA with explicit sRGB, XYZ D65, HSL and OKLab conversion boundaries.
- **V1.25 Base Color Model:** implemented; each component can carry one typed BASE authority with authored/inherited/generated provenance, explicit inheritance/override policy, preserved source sRGB and targeted appearance fingerprinting.
- **V1.26 Palette Model:** implemented; one typed whole-palette authority per component with semantic slots, provenance, inheritance/override rules, canonical colors, persistence and targeted invalidation.
- **V1.27 Effective Appearance Composition:** implemented; BASE and Palette remain separate authorities and composition performs deterministic role selection only, with provenance retained and no color mixing.
- **V1.28 Appearance Role Bridge:** implemented; a typed role contribution now crosses explicitly into the legacy `AppearanceResolutionInput.base_color` field, preserving canonical color, authored representation, authority provenance and targeted invalidation without creating a second authority.
- **V1.29 Typed Appearance Input Promotion:** implemented; a canonical `TypedAppearanceInput` owns the selected role and the BASE domain consumes it directly; legacy `base_color` remains a derived compatibility representation.
- **V1.30 Typed BASE Consumer Migration:** implemented; internal source consumers no longer call the legacy `build_appearance_input()` builder outside the three explicit compatibility/bridge boundaries, and the canonical typed envelope now exposes a direct BASE-domain hand-off.
- **V1.31 Typed COLOR Consumer Migration:** implemented; `TypedColorInput` projects only the selected semantic role into the COLOR domain, the resolver returns canonical `ColorRGBA` unchanged, provenance/dependencies are preserved, and BASE/MATERIAL/LIGHTING leakage plus duplicate legacy COLOR authority are rejected.
- **V1.32 COLOR Consumer Audit:** implemented; the production tree was scanned with AST-aware evidence for `AppearanceDomain.COLOR`, legacy color vocabulary, palette/effect references and color-space conversions. No downstream production caller of the typed COLOR resolver was found.
- **V1.33 COLOR Downstream Closure Audit:** implemented; a conservative production call/import graph proved that the typed COLOR resolver still has zero downstream production callers and zero unresolved dynamic escape hatches.
- **V1.34 First Real Downstream COLOR Operation:** implemented; the existing production `shadow`/`tint` color transformation was traced from `resolve_component()` → `resolve_effects()` and migrated to an explicit canonical `ColorRGBA` boundary. The established encoded-sRGB 8-bit interpolation law is preserved for visual continuity; the result returns to canonical linear-sRGB RGBA, base alpha is preserved, and the legacy string helper remains only as an explicit compatibility adapter.
- **V1.35 VisualEffect COLOR Surface Audit:** implemented; all five production `VisualEffect` kinds were classified, relation/consequence/legacy effect creation paths were audited, `shadow` and `tint` were proven to share the single existing color operation, scalar effects were kept outside COLOR, no distinct second color transform was found, and the provably unreferenced legacy `_apply_shadow` RGB helper was removed after repository-wide call-site proof.
- **V1.36 COLOR Downstream Audit:** implemented as an audit-only checkpoint; six direct `ColorRGBA` consumer files were classified, five non-effect surfaces were traced to authority/compatibility/persistence/validation roles, the existing effect path was kept closed, renderer-local RGBA arithmetic was separated from generic COLOR, eye code was audited independently, zero HSL/OKLab/XYZ operations were found outside the canonical module, and no new generic color transformation was warranted.
- **Gamut policy:** fail-closed; no implicit clipping or gamut mapping.
- **BASE integration:** validated hexadecimal BASE colors now cross the canonical color boundary without changing encoded 8-bit output.
- **Visual QA:** V1.36 runtime board uses actual BASE/Palette COLOR resolution, renderer-local RGBA compositing and an eye SVG/raster sample; it was visually inspected. This remains diagnostic evidence, not production-art or ICC certification.

- **Core vision:** aligned with the permanent general visual-language engine vision.
- **Eye / ocular 3D:** retained as a Golden-Component stress-test branch; not a general 3D engine.
- **Generic transform contract:** repaired so `LocalTransform` contains only generic spatial fields.
- **Ocular transform semantics:** owned by the eye-specific adapter under `components/face/eyes/geometry/`.
- **Persistence compatibility:** legacy V1.13–V1.22 ocular transform fields are migrated into component parameters; conflicting duplicated values fail closed.
- **Documentation synchronization:** re-baselined to this checkpoint.
- **A9 facade budget:** repaired; `render/svg.py` is now within the declared budget.
- **A5/A10 evidence:** current release-gate evidence is regenerated for this checkpoint; historical V1.3 evidence remains immutable provenance.
- **Live PostgreSQL:** environment-dependent and not claimed verified unless a live run is actually performed.
- **Real-pixel calibration:** still closed; no human semantic approval is inferred from diagnostic artifacts.

## Current architectural boundary

```text
GENERIC RUNTIME
    LocalTransform
    hierarchy composition
    world/scene/camera affine transforms
    z accumulation
          │
          ▼
EYE-SPECIFIC ADAPTER
    ocular yaw/pitch
    alignment-axis rotation
    ocular basis composition
          │
          ▼
EYE GEOMETRY
```

The generic runtime must not import `visual_engine.components.face.eyes` and must not
interpret ocular parameter names. Eye-specific code may consume generic transforms and
component parameters through an explicit adapter.

## Current execution order

1. **V1.23 architectural realignment** — preserved as the current generic/ocular boundary baseline.
2. **V1.24 canonical color-space foundation** — implemented and verified.
3. **V1.25 Base Color Model** — implemented and verified.
4. **Current structural release gate** — A4/A5/A6/A7/A8/A9/A10 evidence must remain reproducible from the new checkpoint.
5. **V1.26 Palette Model** — implemented and verified.
6. **V1.27 Effective Appearance Composition Foundations** — implemented and verified after visual review.
7. **V1.28 Appearance Role Bridge** — implemented and verified after visual review.
8. **V1.29 Typed Appearance Input Promotion** — implemented and verified after visual review.
9. **V1.30 Typed BASE Consumer Migration** — implemented; remaining source consumers of the legacy appearance-input builder are now explicitly limited to compatibility boundaries.
10. **V1.31 Typed COLOR Consumer Migration** — implemented; the typed COLOR resolver consumes only the selected semantic role and preserves canonical color/provenance without mixing.
11. **V1.32 COLOR Consumer Audit** — implemented; 170 production Python files and 206 relevant references were classified, with zero downstream production COLOR consumers and zero unclassified findings.
12. **V1.33 COLOR Downstream Closure Audit** — implemented; 1140 production symbols and 1464 direct call edges were analyzed, with one internal resolver-wrapper edge, zero downstream production callers and zero dynamic resolver escape hatches.
13. **V1.34 First Real Downstream COLOR Operation** — implemented; an existing shadow/tint operation is now explicit about its input/output representation, calculation space, alpha behavior, provenance and cache/version boundary. No fabricated typed-COLOR-resolver caller was introduced.
14. **V1.35 VisualEffect COLOR Surface Audit** — implemented; the remaining effect surface was classified, relation/consequence/legacy paths were traced, direct RGB arithmetic outside the canonical color boundary was closed, and no new COLOR algorithm was warranted.
15. **V1.36 COLOR Downstream Audit** — implemented; all direct non-effect `ColorRGBA` surfaces were classified, renderer-local RGBA and eye-reference RGB analysis were kept in their own domains, no new generic transformation was found, and runtime source remained byte-for-byte unchanged from V1.35.
16. **Next generic brick:** discover one distinct real production color transformation only if evidence establishes it; do not bundle or invent operations.
17. **Eye reference calibration** — continue only as a parallel evidence stream when two genuinely human-approved independent samples exist.

## Current appearance boundary

```text
semantic appearance contribution
        ↓
validated domain contract
        ↓
canonical color representation (V1.24)
        ↓
typed BASE authority (V1.25)
        ↓
typed Palette authority (V1.26)
        ↓
renderer-neutral effective composition selection (V1.27)
        ↓
typed appearance role bridge (V1.28)
        ↓
canonical typed appearance input (V1.29)
        ↓
V1.30 typed BASE consumer migration / compatibility isolation
        ↓
BASE domain consumes typed role provenance
        ↓
V1.31 typed COLOR projection + canonical COLOR resolver
        ↓
V1.32 production COLOR consumer audit — no downstream migration target
        ↓
V1.33 downstream closure audit — no production caller / no dynamic escape hatch
        ↓
future COLOR operation only after a real downstream consumer is established
```

The canonical color layer does not perform appearance composition.

## V1.34 evidence boundary

V1.34 changes one existing runtime color-operation seam and therefore bumps engine/package version to 1.3.8 and resolution identity to 18. The migrated operation is limited to shadow/tint effects; no saturation, contrast, vibrance, temperature, palette mixing, lighting or material operation is introduced.

## V1.35 evidence boundary

V1.35 is an audit/cleanup checkpoint and does not change runtime version semantics. It classifies `VisualEffect` into one canonical shadow/tint color operation plus scalar opacity/visibility/occlusion effects, proves relation/consequence/legacy effect creation paths, and removes only the repository-proven unreferenced `_apply_shadow` helper. No new color algorithm is introduced.

## V1.36 evidence boundary

V1.36 is an audit-only checkpoint. It enumerates direct `ColorRGBA` consumers outside the
canonical color-space/effect modules, separates authority/serialization/compatibility/palette/rendering/eye-analysis roles, proves zero new generic COLOR transformations, and verifies byte-for-byte unchanged production runtime Python against the trusted V1.35 checkpoint. The released evidence is self-contained: the 171-file V1.35 runtime SHA-256 fingerprint is retained without restoring superseded V1.35 generated artifacts.

## Explicit non-goals of this checkpoint

- no new ocular optical parameter;
- no additional orbital anatomy;
- no new 3D eyelid physics;
- no automatic semantic inference from reference pixels;
- no calibration promotion from synthetic evidence;
- no generic 3D engine hidden inside the generic transform runtime.
