<!-- Refactored from docs/governance/roadmap/ROADMAP__part_01.md; source lines 1-139; content preserved. -->
<!-- Part 1/16. Use the family index for navigation. -->
# Visual Engine — Master Roadmap

This roadmap is the execution plan derived from the permanent vision in `docs/governance/architecture/ENGINE_VISION__part_01.md`.

> **Authoritative status rule — A4 (2026-09-16):** The historical checkpoint sections below
> are preserved for traceability. The **Current authoritative state** section is the source of
> truth for what is implemented now; historical checkboxes must not be read as current status.

## Current authoritative state — V1.36 COLOR Downstream Audit

The single current status surface is `docs/governance/status/CURRENT_STATUS__part_01.md`. Historical V1.3/A0–A10
sections below remain immutable provenance and are not the current frontier.

- **V1.22:** provenance gate implemented; real-pixel calibration remains correctly closed until two independent human-approved samples exist.
- **V1.23 boundary repair:** implemented; generic `LocalTransform` no longer contains ocular semantics, and generic transform resolution no longer imports or executes eye-specific 3D code.
- **V1.23 persistence migration:** implemented; legacy serialized ocular transform fields are migrated into component parameters with conflict rejection.
- **V1.23 documentation rebaseline:** implemented; current checkpoint and execution order are now explicit.
- **V1.24 canonical color spaces:** implemented; linear-sRGB RGBA is the canonical internal color representation with explicit sRGB, XYZ D65, HSL and OKLab boundaries.
- **V1.24 gamut policy:** fail-closed; no implicit gamut mapping or clipping.
- **V1.24 BASE integration:** canonical color boundary is executed without changing the existing 8-bit hexadecimal BASE output contract.
- **V1.25 Base Color Model:** implemented; typed `BaseColor` authority, authored/inherited/generated provenance, explicit inheritance/override rules, source preservation, alpha semantics, persistence, adversarial rejection and targeted appearance fingerprints are verified.
- **V1.26 Palette Model:** implemented; typed whole-palette authority with `primary/secondary/accent/detail`, source/provenance, inheritance/override, canonical linear-sRGB entries and targeted fingerprints.
- **V1.27 Effective Appearance Composition:** implemented; deterministic BASE-versus-Palette selection by semantic role, provenance retention, explicit modes, fail-closed missing/conflicting inputs and geometry-independent composition fingerprints.
- **V1.28 Appearance Role Bridge:** implemented; typed role contribution crossing into the legacy appearance input without double authority, with exact authored sRGB preservation, provenance, targeted invalidation and adversarial tamper rejection.
- **V1.29 Typed Appearance Input Promotion:** implemented; `TypedAppearanceInput` is the canonical renderer-neutral appearance envelope and the BASE domain accepts the typed role directly.
- **V1.30 Typed BASE Consumer Migration:** implemented; the legacy appearance-input builder is now isolated to explicit compatibility boundaries and internal BASE-domain consumers use the typed envelope directly.
- **V1.31 Typed COLOR Consumer Migration:** implemented; `TypedColorInput` is the minimal typed COLOR projection, the COLOR resolver returns canonical linear-sRGB RGBA unchanged, and COLOR identity excludes geometry/material/renderer state.
- **V1.32 COLOR Consumer Audit:** implemented; AST-aware production audit covers the requested COLOR vocabulary and conversions across 170 Python source files. It found zero downstream typed-COLOR callers, zero unclassified findings, and therefore no legitimate migration target.
- **V1.33 COLOR Downstream Closure Audit:** implemented; conservative production call/import graph proved zero downstream typed-COLOR callers and zero unresolved dynamic resolver escape hatches.
- **V1.34 First Real Downstream COLOR Operation:** implemented; the real generic `shadow`/`tint` operation was migrated to canonical `ColorRGBA` boundaries while preserving the established encoded-sRGB 8-bit visual law.
- **V1.35 VisualEffect COLOR Surface Audit:** implemented; all five `VisualEffect` kinds are classified, relation/consequence/legacy effect creation paths are audited, direct RGB arithmetic outside the canonical color boundary is zero, `shadow`/`tint` share one distinct operation, and the unused `_apply_shadow` helper was removed after repository-wide proof.
- **V1.36 COLOR Downstream Audit:** implemented; 171 production Python files were audited, six direct `ColorRGBA` consumer files were classified, five non-effect surfaces were traced to authority/compatibility/persistence/validation roles, renderer-local RGBA and eye-reference RGB analysis were kept separate, zero HSL/OKLab/XYZ operations were found outside the canonical module, and zero new generic COLOR transformations were proven. Runtime source is byte-for-byte unchanged from V1.35.
- **A5/A9/A10 current closure:** re-established as checkpoint-local evidence, not inferred from historical V1.3 claims.
- **Live PostgreSQL:** environment-dependent and not claimed verified without live evidence.

### Current implementation boundaries

- Generic transform runtime: **IMPLEMENTED**; only generic spatial transforms are interpreted.
- Ocular orientation: **IMPLEMENTED as eye-specific adapter**; no generic-runtime ownership.
- Generic interaction/deformation application: **PLANNED/PARTIAL**.
- Appearance domain contracts plus BASE/MATERIAL resolvers: **IMPLEMENTED foundation**; canonical color spaces are implemented; full appearance intelligence remains planned.
- Production geometry cache SLA: **NOT CLAIMED**.
- Live PostgreSQL: **UNVERIFIED** without a configured live server.


## Phase 0 — Foundation
**Goal:** establish the language of the engine.

- [x] Component/meta-model
- [x] Runtime graph
- [x] Hierarchy
- [x] Relations
- [x] Constraints
- [x] Deterministic seeds
- [x] Provenance
- [x] Versioning
- [x] Resolution fingerprints

## Phase 1 — Geometry Runtime
**Goal:** generate renderer-neutral geometry efficiently.

**Current status:** core geometry contracts, generators, dependency preparation, transform resolution and
versioned geometry-cache identity are implemented. General semantic regions are implemented as the
V1.3 foundation described below; production surface/mesh abstraction remains planned.

- [x] GeometryContract
- [x] Geometry generators
- [x] Generator registry
- [x] Generator dependencies
- [x] Recursive preparation
- [x] Multi-component generation
- [x] Geometry cache
- [x] Local → world → scene → camera transform resolution
- [x] Semantic-region geometry foundation (V1.3)
- [ ] General production semantic geometry regions
- [ ] Production-quality surface/mesh abstraction

## Phase 2 — Generic Visibility / Occlusion / Interaction
**Current status:** visibility/coverage/semantic-region foundations are implemented; generic interaction
consequence application remains a separate gate. This phase is therefore no longer the immediate
"next major phase".

### 2.1 Semantic regions
- [x] `SemanticRegion`
- [x] region hierarchy / region map foundation
- [x] region boundary geometry
- [x] region-local coordinates
- [x] region-to-component mapping
- [x] region dependency graph foundation

### 2.2 Coverage
- [x] `CoverageRegion` / per-region coverage result
- [x] arbitrary-angle partial coverage through planar geometry operations
- [x] top/bottom/left/right/diagonal coverage
- [x] disconnected coverage pieces where represented by the boolean geometry backend
- [x] coverage percentage/area
- [x] depth-aware coverage

### 2.3 Visibility
- [x] geometric visibility (2D planar kernel)
- [x] optical visibility (2D/transmission model)
- [x] opacity
- [x] transmission
- [x] occlusion geometry/boolean clipping at the renderer-neutral kernel boundary
- [x] affected-region resolution / causal attribution boundary

### 2.4 Generic interaction
- [ ] `InteractionEvent`
- [ ] contact
- [ ] collision
- [ ] pressure
- [ ] pulling
- [ ] deformation consequence contracts
- [ ] state/effect consequences

### Acceptance gate
A generic rectangle/polygon/circle must be able to partially cover an eye without knowing that it is an eye, and the resolver must report exactly which semantic eye regions are affected.

## Phase 3 — Color / Appearance Intelligence

**Goal:** eliminate component-specific color hacks.

- [x] canonical color spaces (V1.24)
- [x] base color model (V1.25)
- [x] palette model (V1.26)
- [ ] shadow model
- [ ] highlight model
- [ ] ambient/key/fill/rim/bounce light representation
- [ ] material response
- [ ] roughness
- [ ] metallic response
- [ ] transparency/transmission
- [ ] reflection response
- [ ] style response
- [x] effective appearance composition foundation (V1.27)
- [x] typed appearance role bridge (V1.28)
- [ ] eye visual validation
- [ ] generic object visual validation
