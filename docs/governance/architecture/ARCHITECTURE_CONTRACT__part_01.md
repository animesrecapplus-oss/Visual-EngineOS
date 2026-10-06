<!-- Refactored from docs/governance/architecture/ARCHITECTURE_CONTRACT__part_01.md; source lines 1-142; content preserved. -->
<!-- Part 1/2. Use the family index for navigation. -->
# Visual Engine — Master Architecture Contract

This file is the concise, normative contract. Detailed implementation notes live in the versioned architecture documents and `docs/governance/roadmap/ROADMAP__part_01.md`.

## Non-negotiable separations

```text
IDENTITY    != MORPHOLOGY
MORPHOLOGY  != STYLE
STYLE       != APPEARANCE
APPEARANCE  != STATE
STATE       != EXPRESSION
EXPRESSION  != GAZE
GAZE        != GEOMETRY
GEOMETRY    != OCCLUSION
OCCLUSION   != MATERIAL
MATERIAL    != RENDERER
```

A specialized solver may consume another solver's output, but must not absorb unrelated responsibilities.

## Generic component contract

Every component is addressable by a stable ID and may expose:

```text
Component
├── identity
├── parameters
├── anchors
├── relations
├── constraints
├── profiles
├── state
├── local_transform
├── visual_contract
├── visual_overrides
└── geometry_contract
```

The visual contract includes:

```text
fill color
contour color/width/style/cap/join/opacity
material
opacity
visibility
```

The runtime resolves inherited context into `ResolvedVisualContract` before geometry/rendering.

## Resolution contract

Inheritance is property-specific. Transform composes, depth accumulates, opacity/visibility multiply, while visual fields inherit or override explicitly. `VisualOverrides` uses `None` to mean inherit. Legacy `VisualContract` remains a complete explicit local contract. State precedence is owned by the explicit state-policy resolver; relation propagation and appearance-layer composition remain separate contracts.

## Coordinate contract

Components are authored in local coordinates. Parent transforms are composed before rendering. The human eye pair is authored in the face/head frame so a head in-plane rotation rotates the pair as a single aligned axis.

A 2D head rotation is not a substitute for a 3D head pose. True yaw/pitch/perspective remain future systems.

## Visual consequence contract

An external object can cause independent effects:

```text
object
 ├── occlusion
 └── shadow
       ↓
component
       ↓
descendant visual context
```

Occlusion must not be confused with shadow, transmission or reflection.

A component's effective appearance is derived from base appearance plus resolved visual effects. Source definitions remain immutable.

## Eye-pair contract

For a human face:

- two eyes are the default pair;
- pair-level placement owns the common axis;
- local morphology can remain slightly asymmetric;
- heterochromia is appearance, not identity duplication;
- eye-specific state can differ when explicitly requested;
- a shared head transform preserves pair alignment.

Non-human profiles may relax these constraints deliberately.

## Layering contract

The intended ocular chain is:

```text
HUMAN EYE PAIR
      ↓
EYE PAIR SOLVER
      ↓
GAZE / EYELIDS / EXPRESSION
      ↓
OCULAR STATE
      ↓
APPEARANCE
      ↓
MATERIAL / OPTICS
      ↓
GEOMETRY
      ↓
OCCLUSION / SHADOW
      ↓
RENDERER
```

Higher-level systems must remain above `GazeSolver`:

- 3D convergence;
- expression;
- eyelid deformation;
- optical simulation;
- biological tear system;
- general scene occlusion.

## Data-driven contract

PostgreSQL is the source of truth for reusable definitions, profiles and rules. It is a cold-path dependency. Geometry and rendering code must not issue per-component/per-pixel database queries.

Python owns generic algorithms. PostgreSQL owns reusable data and policy.

## Determinism contract

Persistent/cache identities must never rely on Python's process-randomized `hash()`.

Canonical serialization + SHA-256 is the baseline for stable contract identity. The A3 geometry fingerprint is now an explicit versioned identity contract covering authored geometry and explicitly projected generator inputs, with visual/transform exclusions.

## Definition of done

No feature is declared complete merely because a class exists. Completion requires implementation, tests, documentation, deterministic validation, and visual regression where the feature changes pixels.
