<!-- Refactored from docs/governance/architecture/ENGINE_VISION__part_01.md; source lines 839-968; content preserved. -->
<!-- Part 7/8. Use the family index for navigation. -->
## 24. Architecture layers

The target conceptual architecture is:

```text
                    SCENE ORCHESTRATOR
                            │
             ┌──────────────┼──────────────┐
             ↓              ↓              ↓
        STRUCTURE        GENERATION       PROMPT
             │              │          COMPILER (later)
             ↓              ↓
         RELATIONS       GEOMETRY
             │              │
             └───────┬──────┘
                     ↓
              RESOLUTION LAYER
        ┌────────────┼─────────────┐
        ↓            ↓             ↓
   TRANSFORMS    VISIBILITY    APPEARANCE
                     │             │
                 OCCLUSION     COLOR/MATERIAL
                 INTERACTION    LIGHTING
                     │             │
                     └──────┬──────┘
                            ↓
                          STYLE
                            ↓
                       COMPOSITION
                            ↓
                         RENDER
```

This architecture supersedes any idea of one enormous Python function that directly draws every object.

---

## 25. Non-negotiable engineering rules

1. **No giant monolithic renderer.**
2. **No object-specific explosion of `if/elif` branches for generic systems.**
3. **No mixing identity, pose, state, style and scene placement.**
4. **No mixing geometry generation with appearance resolution.**
5. **No treating partial occlusion as binary visibility.**
6. **No treating color as merely hex darkening.**
7. **No claiming final artistic quality from structural prototypes.**
8. **No random regeneration when persistent identity is required.**
9. **No speculative GPU optimization before profiling.**
10. **No architectural abstraction without a concrete test/use case.**
11. **Every major generic subsystem must be testable independently.**
12. **Every important visual behavior needs a deterministic regression test.**
13. **When a visual interaction is implemented, verify both geometric location and semantic consequence.**
14. **Eye-specific knowledge must remain behind generic contracts.**
15. **Documentation must distinguish IMPLEMENTED, PARTIAL, PLANNED and NON-GOAL.**

---

## 26. Current status at this checkpoint

Implemented foundations include:

- component/meta-model;
- runtime graph;
- hierarchy and relation dependency resolution;
- constraints/provenance/versioning;
- visual effects and state precedence;
- eye morphology and gaze;
- binocular gaze;
- geometry contracts;
- generator registry;
- multi-component generators;
- geometry cache;
- local → world → scene → camera transform/composition resolution;
- SVG eye rendering and visual QA infrastructure.

The following are intentionally **not yet claimed as complete**:

- complete generic interaction/deformation application;
- full interaction/deformation engine;
- production Color/Appearance Intelligence Engine;
- physically based ocular optics;
- production-grade raster antialiasing;
- full prompt compiler;
- production character-art quality;
- full 3D scene/optics;
- animation system.

The semantic-region + partial-coverage + 2D visibility foundation is implemented. The current structural priority is **V1.35 VisualEffect COLOR Surface Audit and checkpoint-local release verification**. Color operations must originate from a real production consumer and an explicit color-space contract; V1.34 establishes the first such seam with shadow/tint effects while keeping the typed COLOR resolver boundary separate. The ocular branch remains a Golden-Component stress test, not the generic architecture.

---

## 27. The original vision must remain the reference

When future implementation choices create tension between a convenient local solution and the general engine vision, consult this document first.

The test is:

> **Does this make the engine more capable of representing arbitrary visual entities through a coherent visual language, or does it merely make the current eye demo easier?**

If it only makes the eye demo easier, it must not silently become the universal architecture.


## V1.3.5 — Spatial relationship and placement invariant

The engine must distinguish two independent questions:

```text
WHERE SHOULD A SOURCE GEOMETRY BE PLACED RELATIVE TO A TARGET?
                                      ↓
                         Spatial Placement Solver
                                      ↓
WHAT PORTION OF THE TARGET IS ACTUALLY OCCLUDED?
                                      ↓
                           Visibility Kernel
```

A qualitative morphology descriptor such as `large` is not a geometric dimension. It must first resolve to actual target geometry. Dependent objects are then placed using explicit geometric relationships, anchors, relative dimensions and/or measured coverage intent.

The placement layer is object-agnostic. No rule may encode `if glasses`, `if hand`, `if hair`, `if eye`, etc. The same spatial contracts must work for arbitrary future components.

Camera zoom is not allowed to alter intrinsic relative placement. Camera projection belongs after geometry and scene placement.

For coverage-driven placement, the solver must measure:

```text
area(source ∩ target) / area(target)
```

rather than infer coverage from names or bounding boxes. If the mathematical preconditions for a reliable search are not satisfied, the resolver must fail closed rather than return a false solution.
