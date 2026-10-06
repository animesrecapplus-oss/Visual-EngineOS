# V1.83 — Eye semantic hierarchy and micro-component ownership matrix

## Purpose

This matrix formalizes the V1.82 parentage correction without promoting planning atoms to
implemented components. It separates four notions that were previously conflated:

1. **semantic parent** — the domain object that owns the child's meaning/attachment;
2. **aggregate parent** — the public/assembly owner that stores or assembles values;
3. **canonical implementation owner** — the source file that actually implements one responsibility;
4. **blueprint atom** — a planned/atomic capability, which is not automatically a micro-component.

A row is `REAL` only when executable ownership and real consumers are evidenced. A missing truth
dossier is a traceability defect, not permission to invent a contract or implementation status.

## Corrected hierarchy

```text
FACE
└── ORBIT / PERIOCULAR FRAME
    ├── EYELID SYSTEM
    │   ├── upper/lower margins
    │   ├── aperture / envelope measurements
    │   ├── folds / canthi / tearline
    │   └── occluder boundary
    ├── LASH SYSTEM                 ← related to eyelid implantation/follow, not a parent chain
    ├── EYEBROW SYSTEM              ← periocular sibling, not an eyelid child
    ├── CARUNCLE
    ├── EPICANTHIC FOLD
    └── EYEBALL
        ├── SCLERA
        ├── IRIS
        │   └── PUPIL[n]
        │       ├── pupil body/specification
        │       ├── outline
        │       └── glow/smoke value children
        └── CORNEA

Cross-relations (not parentage): GAZE, HIGHLIGHT/REFLECTION, OCCLUSION,
TRANSFORM, EXPRESSION, VISIBILITY, CACHE/FINGERPRINT.
```

This hierarchy is grounded by the existing V1.15 and V1.17 contracts: pupil → iris is a
true semantic parent-child relation; orbit/aperture/canthi and eyeball/iris/pupil belong to
different ownership frames. `CMP-EYE` remains the aggregate/public eye-system owner; it is
**not** the direct semantic parent of Pupil.

## Ownership matrix

| Node / micro-component | Type | Semantic parent | Aggregate parent | Canonical owner / evidence | Real consumers | Truth status |
|---|---|---|---|---|---|---|
| `CMP-EYE` | aggregate | FACE | FACE | `components/face/eyes/*` | face composites / public eye API | REAL |
| ORBIT / PERIOCULAR | semantic frame | FACE | CMP-EYE | no standalone owner proven | eyelid/ocular assembly | SEMANTIC NODE; no promotion |
| EYELID | executable value/system | ORBIT/PERIOCULAR | CMP-EYE | `eyelid/spec.py:6-47`; geometry eyelid surface is separate | appearance + generator | REAL; dossier required |
| LASH | executable value/system | ORBIT/PERIOCULAR | CMP-EYE | `lashes/spec.py:6-63`, `lashes/effects.py` | appearance + styles/profiles | REAL; dossier required |
| EYEBROW | executable value/system | ORBIT/PERIOCULAR | CMP-EYE | `eyebrow/spec.py:7-35` | appearance + styles/expression | REAL; dossier required |
| EYEBALL | semantic surface | ORBIT/PERIOCULAR | CMP-EYE | spherical/ocular geometry contracts; no standalone value owner proven | generator / geometry assembly | SEMANTIC NODE; no promotion |
| SCLERA | ocular surface | EYEBALL | CMP-EYE | part of ocular geometry/appearance; no standalone micro-owner proven | generator / appearance | REAL SURFACE; no standalone promotion |
| IRIS | executable value/system | EYEBALL | CMP-EYE | `iris/spec.py:6-31` | appearance + styles + generator | REAL; dossier required |
| `CMP-EYE-PUPIL` | executable micro-component | **IRIS** | CMP-EYE | `pupil/spec.py:9-32` | appearance + styles + generator + compatibility exports | REAL / CERTIFIED V1.82 |
| CORNEA | ocular surface | EYEBALL | CMP-EYE | ocular geometry surface contracts; no standalone value owner proven | geometry assembly | REAL SURFACE; no standalone promotion |
| CARUNCLE | ocular/periocular detail | ORBIT/PERIOCULAR | CMP-EYE | `appearance/caruncle.py` + geometry caruncle owner | appearance/generator | REAL; dossier required if adopted as micro-component |
| EPICANTHIC FOLD | periocular detail | ORBIT/PERIOCULAR | CMP-EYE | `geometry/epicanthic.py` | geometry assembly | REAL; dossier required if adopted as micro-component |
| GAZE | cross-relation system | EYEBALL / ocular assembly | CMP-EYE | `gaze/solver.py:101-...` | generator / ocular resolution | CROSS-RELATION; separate dossier required before promotion |
| HIGHLIGHT | cross-relation system | ocular reflection surface | CMP-EYE | `highlights/spec.py:6-23` | appearance + styles + generator | CROSS-RELATION; not a Pupil child |
| MORPHOLOGY / ENVELOPE | measurement system | ORBIT/PERIOCULAR | CMP-EYE | `morphology/envelope.py:18-120+` | QA/geometry analysis | MEASUREMENT; not anatomical layer |

## Non-linear relationship rules

- `SCLERA → ENVELOPE` is **false**: envelope is a renderer-neutral measurement of resolved
  lid geometry, not an anatomical layer between sclera and lashes.
- `SCLERA → LASH` is **false**: lashes belong to the periocular/lid-related branch.
- `EYELID → LASH → EYEBROW` as a parent chain is **false**: these are sibling/related systems.
- `PUPIL → HIGHLIGHT` as fixed parentage is **false**: highlights have their own ocular/reflection
  relation and may interact with pupil/iris/cornea/camera/light.
- `IRIS → PUPIL` is **true** and explicitly contracted.
- `CMP-EYE → PUPIL` is only an **aggregate ownership** relation, not the direct semantic parent.

## Atom versus micro-component rule

`PUP.containment`, `PUP.gaze_position`, `PUP.lid_relation`, `PUP.reflection_space`, etc.
are blueprint atoms. Their labels do not prove that each has an independent source owner.
Each atom must be mapped to its actual executable owner before it can receive `CMP-*` status.
A future atom owner may therefore be geometry, gaze, highlight, visibility or another system.

The same rule applies to IRI/LID/LAS/BRW/HIL atoms. `IMPLEMENTED_ATOMIC` in the blueprint is
planning/evidence metadata and does not by itself create a micro-component dossier.

## V1.83 correction gate

The V1.82 Pupil dossier is corrected to:

- semantic parent: `CMP-EYE-IRIS` as the semantic component identity;
- aggregate parent: `CMP-EYE`;
- children: `PupilGlowSpec`, `PupilSmokeSpec`;
- cross-relations: gaze, eyelid exposure, transform, highlight, visibility/occlusion;
- no claim that Iris currently has a complete truth dossier unless its own dossier is created and
  validated through the same protocol.

The correction does not change runtime code, geometry, cache identity, database schema, COLOR,
or valid rendered output.
