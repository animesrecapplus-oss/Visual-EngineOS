<!-- Refactored from docs/governance/architecture/ENGINE_VISION__part_01.md; source lines 969-1083; content preserved. -->
<!-- Part 8/8. Use the family index for navigation. -->
## Spatial relationships and dependent placement — V1.3.6

A visual relationship is not equivalent to an occlusion event. The engine must first
resolve where a source belongs relative to a target, using the target's resolved
geometry and explicitly declared spatial constraints. Only then can the visibility
kernel determine which target regions are affected.

The canonical pipeline is:

```text
Relation
  ↓
Placement declaration
  ↓
PlacementIntent
  ↓
Target semantic region (when explicitly declared)
  ↓
Attachment / alignment / dimension / coverage / depth constraints
  ↓
Spatial Placement Solver
  ↓
Resolved source transform
  ↓
Visibility / Boolean Kernel
  ↓
AffectedRegionEvent
```

Qualitative morphology such as `large` is never treated as a pixel dimension. The
morphology/generation layer must first resolve actual geometry. A dependent object
can then use explicit ratios or coverage constraints against that resolved geometry.
This is what allows the same relationship to remain coherent when the target is
small, large, close-up, far away or globally scaled.

Placement remains category-independent. The runtime must not grow branches such as
`if glasses`, `if hair`, `if hand` or `if bandage`. Those categories may eventually
compile into the same generic relation/constraint language through the prompt or
semantic layer.

No anchor or target region is inferred when the current contract cannot establish it
with explicit data. Foundational geometry code must fail closed rather than return a
plausible-looking but unverified placement.

### Spatial placement constraint invariant

Object placement is resolved from explicit geometry and relationships, then checked
against explicit hard spatial constraints. The engine must never silently invent a
trade-off between incompatible constraints. If a hard constraint cannot be
satisfied by the currently defined solver contract, resolution fails explicitly.

### V1.3 spatial closure checkpoint

The engine now has a concrete generic path from a resolved placement to spatial impact: `PlacementSolution → Resolved Source Geometry → Source Semantic Regions → Visibility Kernel → AffectedRegionEvents`. This is a validation milestone for the architecture's central claim: spatial impact is determined by geometry, frames, depth and optical properties rather than by hardcoded knowledge of the source/target object types.


## A4 status synchronization — 2026-09-16

The permanent vision remains normative; implementation status is delegated to the synchronized
roadmap and V1.3 audit ledger. In particular, semantic regions, planar coverage and the generic
2D visibility kernel are no longer future concepts. Their remaining limitations (3D optics,
renderer clipping, production rendering, and complete interaction/deformation application) remain
explicit nonclaims.

## A10 structural-hardening closure — 2026-09-16

A0–A10 form the current structural hardening baseline for V1.3. A10 is an independent second audit rather than a
repeat of the A9 adversarial suite: it verifies that architecture, contracts, canonical implementation ownership,
compatibility facades, imports, documentation, version policy, migration ordering, persistence claims, cache/geometry
identity and renderer-facing boundaries still agree after all prior changes.

This closure is bounded. It does not claim production rendering quality, complete 3D optics, live PostgreSQL,
exhaustive fuzzing/formal verification, full interaction/deformation, production color/lighting intelligence,
prompt compilation or animation.

## V1.4 eye-deepening frontier — 2026-09-16

Following A10 structural closure, the eye is now developed through the atomic/subatomic blueprint rather than broad
phase labels. The permanent target is a valid parameter manifold: a clean default eye plus very large controlled variation,
with explicit relationships between morphology, iris/pupil structure, lids, lashes, brows, highlights, colour,
expression, camera, prompt semantics, interaction and renderer evidence.

The execution and acceptance discipline is defined in `docs/components/eyes/blueprint/V1.4_EYE_EXECUTION_PROTOCOL.md`; the inventory is owned by
`docs/components/eyes/blueprint/index.json`. This is an execution framework, not a claim that the listed future capabilities
already exist.


## V1.33 — COLOR Downstream Closure Audit

The COLOR resolver boundary is now treated as a closed dependency seam until a real production caller is established. The generic architecture must not manufacture a downstream operation merely to advance the version. A future COLOR transformation must begin from a proven caller and specify input space, calculation space, output space, alpha semantics, gamut policy, provenance, lineage, dependency fingerprint, invalidation, caching and visual acceptance before implementation.


## V1.34 — First Real Downstream COLOR Operation

V1.33 established that the typed COLOR resolver had no production caller. V1.34 therefore traces a different, genuinely reachable color transformation already used by generic component resolution: `resolve_component → resolve_effects → shadow/tint color operation`. The operation now accepts canonical `ColorRGBA` at its boundaries, performs its deliberately preserved encoded-sRGB 8-bit interpolation in an explicit calculation space, and returns canonical linear-sRGB RGBA. The operation preserves the target alpha and does not treat effect-color alpha as a second opacity authority.

This does **not** make shadow/tint part of the typed COLOR resolver. It is a downstream visual-effect operation with its own contract, provenance and version identity. No saturation, contrast, vibrance, temperature, palette mixing, lighting or material response is implied by this checkpoint.


## V1.35 — VisualEffect COLOR Surface Audit

V1.35 closes the remaining generic effect-color ambiguity after V1.34. The production effect vocabulary is explicitly partitioned: `shadow` and `tint` are two entry kinds for the single `effect.color.srgb8-interpolation` operation; `opacity`, `visibility`, and `occlusion` remain scalar visibility/opacity effects and are not COLOR transforms. Relation-generated, consequence-generated and legacy-shadow effect creation paths are audited explicitly. Direct encoded-RGB arithmetic outside the canonical effect/color-space boundary is prohibited; the previously unreferenced `_apply_shadow` helper was removed after repository-wide call-site proof. No second color algorithm is invented when none is present.

## V1.36 — COLOR downstream closure — 2026-09-24

V1.36 confirms that the canonical COLOR layer must remain intentionally small until a real
production transformation exists. Direct `ColorRGBA` consumers are now explicitly separated into
BASE/Palette authority, persistence, validation, compatibility bridge and the already-closed
VisualEffect path. Renderer-local normalized RGBA compositing remains renderer-owned, while the
eye domain remains stylistically independent from generic `ColorRGBA`.

No new generic color algorithm is justified by the current evidence. This preserves the permanent
architectural rule: **do not convert a representation boundary, authority-selection step or
renderer operation into a generic COLOR feature merely because it contains color arithmetic or
color-named fields.**
