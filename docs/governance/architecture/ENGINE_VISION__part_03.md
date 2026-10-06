<!-- Refactored from docs/governance/architecture/ENGINE_VISION__part_01.md; source lines 281-423; content preserved. -->
<!-- Part 3/8. Use the family index for navigation. -->
## 8. Relations are as important as hierarchy

The engine must model semantic and geometric relations such as:

```text
STRUCTURAL
SPATIAL
ANATOMICAL
GEOMETRIC
CONTACT
OCCLUSION
ATTACHMENT
DEFORMATION
CAUSAL
EXPRESSIVE
SEMANTIC
```

Relations create dependency paths and consequences.

Example:

```text
Hand CONTACT Face
Hand OCCLUDES Eye
Finger PULLS Skin
Skin DEFORMS FaceSurface
FaceSurface AFFECTS Eyelid
Eyelid AFFECTS EyeOpening
EyeOpening AFFECTS Expression
```

The dependency system must therefore understand more than parent/child ancestry.

---

## 9. Permanent rule for interactions

Every visual interaction must be resolved in two conceptual stages:

### Stage A — geometric interaction

Determine **where** the interaction occurs:

- intersection;
- contact;
- overlap;
- distance;
- depth relation;
- penetration;
- coverage geometry;
- deformation area.

### Stage B — semantic consequence

Determine **which semantic regions/components** are affected and what follows:

```text
GEOMETRY
  ↓
AFFECTED REGIONS
  ↓
STATE / RELATION CONSEQUENCES
  ↓
APPEARANCE CONSEQUENCES
  ↓
RENDER
```

Never encode this as a giant list of object-specific `if/elif` rules.

---

## 10. Partial occlusion is a generic system

An occluder may cover only part of a target.

Coverage can occur:

- top;
- bottom;
- left;
- right;
- diagonal;
- at arbitrary angle;
- across multiple disconnected regions;
- with partial transparency.

The engine must not reduce this to `eye.visible = false`.

Conceptual contract:

```text
OcclusionQuery
├── occluder_id
├── target_id
├── intersection_geometry
├── depth_relation
├── opacity
└── transmission

OcclusionResult
├── affected_regions
├── visibility
├── transmitted_visibility
├── coverage
└── consequences
```

The affected regions are discovered from geometry + semantic region boundaries, not from the name/type of the occluding object.

For an eye, a single partial occluder may affect some combination of:

- upper eyelid;
- lower eyelid;
- eyelashes;
- eyebrow;
- sclera;
- iris;
- pupil;
- highlights;
- tear film;
- surrounding face region.

The resolver must determine the actual affected subset.

### Visibility is not the same as opacity

These concepts remain separate:

```text
GEOMETRIC COVERAGE
OPTICAL VISIBILITY
OPACITY
TRANSMISSION
REFLECTION
REFRACTION
```

A transparent object can geometrically cover a region while leaving part of the underlying object optically visible.

---
