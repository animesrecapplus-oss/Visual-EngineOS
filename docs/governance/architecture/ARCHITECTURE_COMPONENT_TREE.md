# Component architecture tree

## Rule

The directory structure follows the semantic ownership of the visual entity, not the chronology in which the code was written.

Shared infrastructure belongs in `components/common`.

Face-specific components belong in `components/face`.

Eye-specific systems belong under `components/face/eyes`.

## Current tree

```text
components/
├── common/
│   ├── meta.py
│   ├── visual_contract.py
│   └── geometry_contract.py
│
└── face/
    └── eyes/
        ├── core.py
        ├── pair.py
        ├── expression.py
        ├── profiles.py
        ├── styles.py
        ├── pupil/
        ├── iris/
        ├── eyelid/
        ├── lashes/
        ├── eyebrow/
        ├── highlights/
        └── effects/
```

## Intended future expansion

```text
face/
├── eyes/
│   ├── pupil/
│   ├── iris/
│   ├── eyelid/
│   ├── lashes/
│   ├── eyebrow/
│   ├── highlights/
│   └── effects/
├── ears/
├── nose/
├── mouth/
├── chin/
├── cheeks/
├── forehead/
├── skull/
├── hair/
└── neck/
```

These future directories are created when their systems become real implementation targets; empty speculative directories are avoided.

## Ownership rule

A concept has one implementation owner.

Legacy import paths may re-export the owner for compatibility, but no duplicate implementation is allowed.

## Common versus component-specific

Common:

- transforms;
- geometry contracts;
- generic visual contracts;
- metadata;
- generic constraints/relations;
- deterministic hashing/versioning;
- shared rendering abstractions.

Eye-specific:

- ocular morphology;
- gaze;
- pupil;
- iris;
- eyelids;
- lashes;
- eyebrows;
- ocular highlights;
- ocular effects;
- eye-pair logic;
- ocular presentation profiles.

## Migration policy

The current `geometry/eye*.py` and `model/*.py` files are compatibility facades. They should not receive new domain logic. New eye logic belongs in `components/face/eyes`; new shared component infrastructure belongs in `components/common`.

The migration rule is one-way: establish one implementation owner first, then keep the historical import path as a thin re-export until callers have migrated.

## Runtime micro-component ownership

`CMP-RUNTIME-STATE-POLICY-CONTRACT` is owned by `runtime/state_policy_contract.py`. The historical `runtime/state_policy.py` remains the state-resolution algorithm owner and compatibility facade; it must not duplicate the value contracts.
`CMP-RUNTIME-GEOMETRY-TRANSFORM-RESOLUTION` is owned by `runtime/geometry_transform_resolution.py`. `runtime/geometry_transform.py` remains the GeometryContract frame-transformation owner and compatibility facade.
`CMP-RUNTIME-PLACEMENT-COVERAGE` is owned by `runtime/placement_coverage.py`. `runtime/placement.py` remains the general placement owner and compatibility surface.
`CMP-RUNTIME-VISIBILITY-BOOLEAN` is owned by `runtime/visibility_boolean.py`. `runtime/visibility.py` remains the depth/optical visibility owner and compatibility surface.
`CMP-RUNTIME-PLACEMENT-CONSTRAINT-CONTRACT` is owned by `runtime/placement_constraints_contract.py`. `runtime/placement_constraints.py` remains the placement-constraint validation/resolution owner and compatibility surface.
`CMP-RUNTIME-PLACEMENT-CONTRACT` is owned by `runtime/placement_contract.py`. `runtime/placement.py` remains the placement solver/materialization owner and compatibility surface.

## V1.78 face visual calibration ownership

The default HumanFace calibration remains owned by the existing face entity and component geometry owners. No generic renderer or runtime ownership is introduced. `hair.py` owns hair silhouette/detail geometry; `generators.py` retains the existing nose geometry owner; `entities/face.py` owns default face-child anchors and authored defaults.

## V1.79 face granularity boundary

The V1.79 audit confirms that `Head` is currently an embedded `HEAD` surface owned by the HumanFace generator, not a standalone child component. `Skull`, `ScalpBoundary`, `Hairline`, `HairMassSections`, `HairStrands`, `OralRegion`, `Chin`, `Cheeks` and `Forehead` are not promoted to source owners without real consumers and contracts.

The operational matrix is `docs/governance/architecture/FACE_GRANULARITY_MATRIX__V1.79.md`. The horizontal development rule is `docs/governance/architecture/FACE_HORIZONTAL_PROGRESSION_POLICY__V1.79.md`.

The first missing real dossier found by the audit is `docs/components/face/nose/`, for the already implemented Nose owner. This closes traceability without creating a new runtime owner.

## V1.80 — mature micro-component selection

The V1.80 audit selected the existing `Ear` leaf as a different mature micro-component from the V1.79 Nose scope. `Ear` already has a real source owner, parent, sibling relations, production composite consumer, cache path, persistence path and focused tests. V1.80 hardens only its leaf input boundary. No new Ear child, inner-ear morphology or Hair subcomponent is promoted.

The proposed Hair order remains architectural planning only: `cranium → scalp boundary → hairline → masses → sections/locks → strands → density → flow → depth/occlusion`. No item in that proposal is promoted to `IMPLEMENTED` by V1.80.

## V1.81 face boundary note

`HumanFace/mouth` remains a leaf owner. V1.81 strengthens only its malformed input boundary; the proposed oral-region
and lip subcomponents remain planning metadata until each has an executable owner and real consumer.

## V1.82 — mature Eye/Pupil micro-component boundary

`CMP-EYE-PUPIL` is a real micro-component semantically owned by Iris and aggregated publicly by `CMP-EYE`. Its canonical local specification owner is
`src/visual_engine/components/face/eyes/pupil/spec.py`; pupil effects remain value children of the package.
V1.82 hardens only the PupilSpec input boundary. Pupil/iris, pupil/gaze, pupil/eyelid and pupil/transform
relations remain downstream contracts and are not promoted by this brick. The direct semantic relation is `IRIS → PUPIL`; `CMP-EYE` is the aggregate/public parent only. Eyelid, lashes and eyebrow are sibling/related periocular systems, not a single parent chain. Highlight is a cross-relation, not a fixed Pupil child. The morphology envelope is a measurement layer, not an anatomical layer. No Hair structural child is promoted.
