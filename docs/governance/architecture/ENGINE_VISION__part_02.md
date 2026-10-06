<!-- Refactored from docs/governance/architecture/ENGINE_VISION__part_01.md; source lines 137-280; content preserved. -->
<!-- Part 2/8. Use the family index for navigation. -->
### 3.4 Style — how is the visual language interpreted?

Style is not identity and is not anatomy.

A stable structural model may be rendered through different style profiles such as:

- realistic;
- anime;
- manga;
- cel shading;
- 3D game;
- cartoon;
- graphic;
- painting;
- custom styles.

Changing style must not require reconstructing the entity from zero.

---

## 4. Identity, structure, state, pose and style are different things

These distinctions are mandatory:

```text
IDENTITY  !=  STYLE
STRUCTURE != APPEARANCE
APPEARANCE != STATE
POSE      != DNA
POSITION  != IDENTITY
SCENE     != ENTITY
```

A character must remain the same character when its:

- pose changes;
- expression changes;
- clothing changes;
- style changes;
- scene changes;
- lighting changes;
- camera changes;
- temporary state changes.

The persistent identity stores the invariant or versioned visual genome; scene instances store contextual placement and state.

---

## 5. Recursive atomicity

Every entity must be decomposable recursively into components until the chosen level of visual control is reached.

Example:

```text
Eye
├── Eyeball
│   ├── Sclera
│   ├── Conjunctiva
│   ├── Cornea
│   ├── Iris
│   │   ├── IrisBase
│   │   ├── IrisPattern
│   │   ├── IrisPigmentation
│   │   └── IrisEdge
│   ├── Pupil
│   └── LimbalRing
├── Eyelids
├── Eyelashes
├── TearSystem
├── Surrounding
└── Vessels
```

A component is not just a shape. It is a controllable visual unit with parameters, geometry, appearance, state, relations and constraints.

The component model must support, where meaningful:

- size;
- shape;
- color;
- contour/stroke;
- depth;
- position;
- orientation;
- curvature;
- asymmetry;
- texture;
- material;
- state;
- visibility;
- relations;
- constraints;
- style transformations.

---

## 6. Grammar + parameters + constraints = controlled infinite variation

"Infinite" procedural generation does not mean arbitrary random values.

The generation space comes from the combination of:

```text
GRAMMAR
+ PARAMETER RANGES
+ MORPHOLOGIES
+ RELATIONS
+ HARD CONSTRAINTS
+ SOFT CONSTRAINTS
+ STATISTICAL PRIORS
+ AESTHETIC PRIORS
+ STYLE PROFILES
+ STATE
+ SEED
```

The same grammar can generate many valid entities while preserving anatomical, geometric and semantic coherence.

Randomness must be deterministic when a seed is supplied.

---

## 7. Constraints are first-class

The engine must distinguish:

- **HARD** — must never be violated;
- **SOFT** — preferred, but resolvable;
- **STATISTICAL** — distributional prior;
- **AESTHETIC** — visual preference, never an absolute law.

Examples:

- a HumanFace profile has two eyes, one nose and one mouth;
- a pupil must remain inside its iris/aperture according to the chosen ocular model;
- a child component must remain in a valid parent region;
- clothing must obey allowed/forbidden regions;
- impossible placements must be rejected or resolved, not silently drawn.

Golden ratio/Fibonacci-like proportions are optional aesthetic priors, never universal anatomy rules.

---
