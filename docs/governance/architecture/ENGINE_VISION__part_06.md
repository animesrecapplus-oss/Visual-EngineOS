<!-- Refactored from docs/governance/architecture/ENGINE_VISION__part_01.md; source lines 692-838; content preserved. -->
<!-- Part 6/8. Use the family index for navigation. -->
## 19. Geometry fidelity roadmap

Simple geometry is only the beginning.

The expected fidelity ladder is:

```text
primitives
  ↓
curves
  ↓
surfaces
  ↓
meshes
  ↓
subdivision
  ↓
textures
  ↓
procedural textures
  ↓
volumetric data
  ↓
material models
```

The engine must not claim photographic reconstruction capability while only implementing primitive SVG geometry.

---

## 20. Prompt compiler — final interaction model

The long-term user-facing flow is:

```text
PROMPT
  ↓
Semantic Interpretation
  ↓
Visual Specification
  ↓
Entity Graph
  ↓
Parameters / Morphology
  ↓
Generators
  ↓
Resolvers
  ↓
Composition / Camera
  ↓
Renderer
  ↓
IMAGE / SVG / ANIMATION
```

A prompt such as "anime character, tired, wet hair, one hand covering the left eye" must eventually compile into explicit structure, state, relations, geometry, appearance and composition rather than a hidden monolithic drawing procedure.

---

## 21. Animation is part of the same language, later

The original design must remain compatible with animation.

The intended common vocabulary is:

```text
Shape
Geometry
Transform
Material
Color
Light
State
Interaction
Animation
Composition
```

The same object that knows how to be represented visually should eventually know how its parameters evolve through time.

Future animation primitives include:

- time;
- keyframes;
- easing;
- velocity;
- spring/overshoot;
- deformation;
- state transitions;
- procedural motion;
- interaction-driven motion.

Do not build the animation engine now at the expense of the core visual representation architecture, but do not design current APIs in a way that blocks it.

---

## 22. PostgreSQL and the knowledge layer

PostgreSQL is the source of truth for persistent visual knowledge, definitions and generated identity.

It should hold structured data such as:

- component definitions;
- parameters;
- anchors;
- relations;
- constraints;
- rules;
- profiles;
- appearance layers;
- states;
- styles;
- interaction rules;
- pose/expression definitions;
- coverage rules;
- entity identities;
- entity versions;
- scene definitions/instances;
- generation runs;
- render artifact metadata.

PostgreSQL is **not** the per-pixel render loop.

Use relational structure for important invariants and controlled JSONB where extensibility is justified.

---

## 23. Cache and determinism

Geometry caching is a first-class performance subsystem.

Cache keys must depend on actual geometry inputs and relevant dependencies, not visual-only changes.

A visual-only change such as color or material should not rebuild unchanged geometry.

Cache boundaries include:

- generator identity/version;
- schema/resolution version;
- geometry inputs;
- relevant hierarchy/relation dependencies.

Failed builds must not poison the cache.

---
