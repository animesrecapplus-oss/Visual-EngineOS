<!-- Refactored from docs/governance/roadmap/ROADMAP__part_01.md; source lines 235-378; content preserved. -->
<!-- Part 3/16. Use the family index for navigation. -->
## Current execution order

```text
V1.24 — Canonical color-space foundation — IMPLEMENTED
  ↓
V1.25 — Base Color Model — IMPLEMENTED
  ↓
V1.26 — Palette Model — IMPLEMENTED
  ↓
V1.27 — Effective Appearance Composition — IMPLEMENTED
  ↓
V1.28 — Appearance Role Bridge — IMPLEMENTED
  ↓
V1.29 — Typed Appearance Input Promotion — IMPLEMENTED
  ↓
V1.30 — Typed BASE Consumer Migration — IMPLEMENTED
  ↓
V1.31 — Typed COLOR Consumer Migration — IMPLEMENTED
  ↓
V1.32 — COLOR Consumer Audit — IMPLEMENTED / NO MIGRATION TARGET WARRANTED
  ↓
V1.33 — COLOR Downstream Closure Audit — IMPLEMENTED / NO DOWNSTREAM CALLER PROVEN
  ↓
V1.34 — First Real Downstream COLOR Operation — IMPLEMENTED / SHADOW-TINT ONLY
  ↓
V1.35 — VisualEffect COLOR Surface Audit — IMPLEMENTED / ONE COLOR OPERATION
  ↓
V1.36 — COLOR Downstream Audit — IMPLEMENTED / NO NEW GENERIC TRANSFORMATION
  ↓
A5/A6/A7/A8/A9/A10 — Current checkpoint release gate — VERIFY
  ↓
General engine progression — dependency-driven
  ↓
Color / Appearance Intelligence — Effective appearance composition and renderer-neutral role bridge
  ↓
Generic Morphology / Expression / Pose as dependencies require
  ↓
Style
  ↓
Identity / Persistence expansion
  ↓
Prompt Compiler
  ↓
Production Rendering
  ↓
Animation
```

The eye calibration branch remains parallel evidence work and does not determine the general
execution order unless a downstream generic contract explicitly depends on a measured ocular value.

The order can change only with an explicit architectural decision and documentation update.

---

## Current checkpoint — V1.3 Semantic Regions / Partial Coverage

**Implemented:** `SemanticRegion`, `RegionMap`, generic `Occluder`, `DepthRelation`,
per-region geometric coverage and transmission reporting.

The system now establishes the required architectural boundary:

```text
geometry → coverage → semantic regions → future consequences → appearance → render
```

The current implementation is intentionally a foundation, not a production
visibility solver. It is exact for convex polygon clipping and approximates
ellipses with deterministic polygons. Multi-occluder overlap, concave boolean
geometry, Bézier intersection and subpixel visibility remain explicit next work.

See `docs/runtime/visibility/V1.3_SEMANTIC_REGIONS_COVERAGE__part_01.md` (split document; see adjacent parts).

## Current checkpoint — V1.3 Region Map Spatial Resolution

**Implemented:** provider-based semantic region attachment and spatial resolution.
Regions are generated from component geometry through a renderer-independent provider,
then transformed with the existing local → world → scene → camera contract.

**Next:** replace the foundation clipping kernel with a robust geometry/boolean layer,
then introduce correct multi-occluder visibility and structured affected-region events.

## Current checkpoint — V1.3 Geometry Boolean / Visibility Kernel

**Implemented:** robust planar primitive conversion, union, intersection, difference,
concave polygon handling, overlap-safe multi-occluder coverage, optical visibility,
separate transmission, deterministic depth ordering, and structured affected-region events.

The visibility kernel is now a real geometric layer rather than the earlier convex
pairwise clipping foundation. It still deliberately stops before 3D optics, Bézier
area tessellation, renderer clipping, and material/color response.

## Current checkpoint — V1.3.4 Generic Consequence Resolution

**Implemented:** declarative event-to-consequence matching over semantic region
properties and visibility measurements. The resolver is generic and does not know
anatomical or occluder categories; it emits typed requests instead of mutating the
scene.

**Next:** build the independent Color / Appearance Intelligence foundation. It must
remain separate from geometry, visibility and consequence resolution.

## V1.3.5 — Generic spatial placement checkpoint — 2026-09-14

Implemented `runtime/placement.py` as the next architectural layer after visibility/consequence resolution.

### What was implemented

- explicit source/target anchor references;
- geometry-relative dimension constraints;
- uniform and non-uniform scale modes;
- arbitrary rotation and numeric offset;
- explicit front/behind/coplanar depth relation;
- geometric coverage intent with deterministic uniform-scale search;
- coverage measurement from actual polygon intersection area;
- fail-closed preconditions for coverage monotonicity;
- immutable `PlacementSolution` with affine matrix and point transformation;
- no object-type-specific placement logic.

### Important design decisions

1. Placement and visibility remain separate. Placement answers **where**; visibility answers **what is covered**.
2. Morphology must resolve before dependent placement. Descriptors such as `large` are not dimensions.
3. Dimension and coverage constraints are mutually exclusive in this first contract. No hidden precedence is allowed.
4. Coverage solving requires the source and target anchors to belong to their respective positive-area regions. This is an explicit numerical precondition rather than an unverified monotonicity assumption.
5. The solver is renderer-independent and works only on `GeometryContract` data.

### Verification

- full `pytest -q`: PASS;
- `python -m compileall -q src`: PASS;
- placement-specific tests cover anchor/rotation, relative dimensions, coverage solving, invalid constraints and deterministic transform evaluation.

### Remaining work

- integrate placement intents with the generic relation graph;
- add explicit directional/attachment/clearance/contact contracts;
- resolve placement against semantic regions rather than only whole target geometry;
- support multi-constraint deterministic solving;
- add collision/penetration handling;
- connect placement results to dependency fingerprints/invalidation;
- only then integrate prompt semantics;
- persistence schema remains deferred until the placement contract is stable.
