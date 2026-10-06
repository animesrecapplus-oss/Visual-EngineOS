# Component roadmap — CMP-FACE-MOUTH

## Completed V1.55

1. canonical renderer-neutral Mouth geometry;
2. real HumanFace child parameters and authored appearance;
3. production registry extension;
4. explicit HumanFace composite with Nose + Mouth dependencies;
5. multi-occluder production visibility;
6. cache invalidation proof;
7. persistence round-trip proof without schema change;
8. hostile API/topology/visibility tests;
9. front/±12° and visibility interaction QA.

## Completed V1.81

1. fresh mature-component audit after V1.80 Ear;
2. pre-change malformed-state reproduction;
3. leaf-owned numeric/non-boolean/finite validation;
4. positive representable-radius guard;
5. hostile, production, parent/sibling and persistence regression;
6. valid-render invariance evidence;
7. exact line-range truth update.

## Deferred

Lip morphology, upper/lower lip decomposition, commissures, teeth, tongue, expression deformation, wetness,
blood/damage states and detailed material/light behaviour remain separate future micro-components.
They are not implemented by V1.81.
