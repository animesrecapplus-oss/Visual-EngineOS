<!-- Refactored from docs/governance/architecture/ENGINE_VISION__part_01.md; source lines 424-569; content preserved. -->
<!-- Part 4/8. Use the family index for navigation. -->
## 11. Color is a separate engine

Color must never become a collection of ad-hoc hex values or component-specific darkening formulas.

The long-term Color/Appearance system must model the transition from illumination to perceived appearance.

Conceptual engine:

```text
COLOR / APPEARANCE INTELLIGENCE
├── ColorSpace
├── BaseColor
├── Palette
├── ShadowModel
├── HighlightModel
├── AmbientLight
├── RimLight
├── BounceLight
├── Contrast
├── Saturation
├── Vibrance
├── Temperature
├── MaterialResponse
├── TransmissionResponse
├── ReflectionResponse
└── StyleResponse
```

The same base color can therefore produce materially different results:

```text
red + matte
red + glossy
red + metallic
red + wet
red + translucent
```

Color is consumed by all components, but it is not owned by any one component.

---

## 12. Appearance resolution pipeline

A component's final appearance should eventually be resolved through a compositional pipeline similar to:

```text
Base Appearance
      ↓
Material
      ↓
Lighting
      ↓
Shadow / Occlusion
      ↓
Transmission
      ↓
Reflection
      ↓
Emission
      ↓
Style Response
      ↓
Effective Appearance
```

This is intentionally separate from geometry generation.

---

## 13. The Eye is the Golden / Reference Component

The eye is the first deep component because it exposes almost every difficult subsystem at once.

It is **not** the final goal of the project.

It is the stress-test component for:

- recursive atomicity;
- morphology;
- constraints;
- local/world transforms;
- gaze;
- expression;
- eyelid deformation;
- lashes;
- eyebrows;
- optical layers;
- partial occlusion;
- semantic regions;
- material;
- color;
- reflection;
- transparency;
- state;
- effects;
- geometry generation;
- caching;
- persistence;
- style.

### Critical rule

Eye-specific implementation may use ocular knowledge, but generic infrastructure must remain generic.

Do not contaminate the universal interaction/occlusion/color/appearance architecture with eye-only branches.

### Current visual status

Current eye renderings are **structural/vector prototypes**, not final anime artwork or production-quality character art. They prove architecture and geometry behavior; they do not yet represent the final visual quality target.

This distinction must remain explicit in project documentation and QA reports.

---

## 14. Generation vs Resolution

These are different responsibilities.

### Generators

Generate intrinsic entity/component geometry from:

- component definition;
- parameters;
- morphology;
- structural context;
- generator dependencies;
- deterministic seed.

### Resolvers

Apply contextual consequences:

- transform/composition resolver;
- visibility/occlusion resolver;
- appearance resolver;
- expression resolver;
- pose resolver;
- style resolver;
- interaction/effect resolver.

This separation prevents every generator from becoming a giant context-aware function.

---
