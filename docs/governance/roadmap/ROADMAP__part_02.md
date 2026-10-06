<!-- Refactored from docs/governance/roadmap/ROADMAP__part_01.md; source lines 140-234; content preserved. -->
<!-- Part 2/16. Use the family index for navigation. -->
## Phase 4 — Morphology / Expression / Pose

- [ ] generic morphology model
- [ ] anatomical constraints
- [ ] deformation system
- [ ] expression solver
- [ ] pose solver
- [ ] gaze-driven deformation
- [ ] hand/face interaction
- [ ] balance/contact constraints

## Phase 5 — Style Engine

Target profiles:

- [ ] anime
- [ ] manga
- [ ] cel shading
- [ ] 3D game
- [ ] realistic
- [ ] cartoon
- [ ] graphic/custom

Style must transform appearance and, where appropriate, controlled geometry priors without duplicating the entity model.

## Phase 6 — Identity / Persistence / Visual Genome

- [ ] stable entity identity API
- [ ] morphology/parameter genome persistence
- [ ] entity versions
- [ ] scene instances
- [ ] generation runs
- [ ] reproducible regeneration
- [ ] spatial selection → exact entity ID
- [ ] PostgreSQL schema expansion

## Phase 7 — Prompt Compiler

```text
Prompt
→ semantic interpretation
→ visual specification
→ entity graph
→ constraints
→ parameters
→ generators
→ resolvers
→ composition
→ render
```

- [ ] visual vocabulary
- [ ] structured intermediate representation
- [ ] prompt-to-parameter mapping
- [ ] ambiguity handling
- [ ] validation
- [ ] deterministic seed handling
- [ ] prompt provenance

## Phase 8 — Production Rendering

- [ ] robust SVG backend
- [ ] CPU raster backend
- [ ] high-quality antialiasing
- [ ] hybrid vector/raster pipeline
- [ ] advanced materials
- [ ] procedural textures
- [ ] advanced surfaces/meshes
- [ ] GPU backend only after profiling

## Phase 9 — Animation

- [ ] time model
- [ ] keyframes
- [ ] easing library
- [ ] spring/overshoot
- [ ] procedural motion
- [ ] state transitions
- [ ] deformation animation
- [ ] interaction-driven animation
- [ ] reusable motion grammar

## Permanent QA policy

Every phase must contain:

1. unit tests;
2. integration tests;
3. deterministic regression tests;
4. visual QA where visual behavior is involved;
5. performance measurement where runtime cost matters;
6. explicit status: `IMPLEMENTED`, `PARTIAL`, `PLANNED`, or `NON-GOAL`.

No visual screenshot is considered proof of production quality by itself.
