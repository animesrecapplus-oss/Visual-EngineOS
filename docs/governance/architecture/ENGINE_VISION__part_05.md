<!-- Refactored from docs/governance/architecture/ENGINE_VISION__part_01.md; source lines 570-691; content preserved. -->
<!-- Part 5/8. Use the family index for navigation. -->
## 15. Persistence and visual identity

Generated entities must be reusable.

A generated character/person is not recreated randomly when the user asks for it again.

The persistent identity should capture, as appropriate:

```text
entity_id
seed
profile
visual genome / morphology
component parameters
constraints
relations
appearance
material
style
state
version
provenance
engine_version
schema_version
```

A scene instance stores contextual information such as:

- pose;
- placement;
- camera;
- depth;
- visibility;
- local state.

Example:

```text
Generation
├── Person_0001
├── Person_0002
├── ...
└── Person_0030
```

If the user later selects "the 20th from the left", spatial ordering resolves to the exact persistent entity ID. The engine then reuses that identity rather than regenerating a new random person.

---

## 16. Scene, composition and camera are separate from entity identity

The same entity may appear in many scene instances.

Composition must support:

- frame;
- camera;
- viewport;
- placement;
- scale;
- depth;
- spacing;
- packing;
- overlap;
- safe areas;
- off-frame entry/exit;
- partial visibility;
- perspective later.

For one object, the frame can zoom appropriately. For many objects, composition must adapt without changing their identities.

---

## 17. Transform chain

The canonical spatial pipeline is:

```text
LOCAL
  ↓
WORLD
  ↓
SCENE
  ↓
CAMERA
  ↓
RENDER SPACE
```

Local geometry must not be double-transformed by generators and component placement.

The transform system is spatial infrastructure; it does not pretend to provide full 3D optics or perspective until those systems actually exist.

---

## 18. Rendering architecture

Python orchestrates. Rendering backends execute.

Target backends:

```text
VECTOR / SVG
CPU RASTER
HYBRID
GPU (later, only when justified)
```

The same resolved scene representation should feed multiple renderers.

CPU implementation should favor:

- NumPy/vectorized operations;
- cached geometry;
- reusable subgraphs;
- bounded memory;
- no Python per-pixel loops.

GPU work should follow profiling, not speculation.

---
