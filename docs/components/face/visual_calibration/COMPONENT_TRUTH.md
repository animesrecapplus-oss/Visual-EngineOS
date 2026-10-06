# Truth — CMP-FACE-VISUAL-CALIBRATION

## Identity

- `CMP-FACE-VIS-001`
- Scope: default HumanFace visual calibration only.
- Canonical owners remain the existing face, hair and nose geometry owners.

## Responsibility

Correct empirically observed default proportions and verify existing component variation through real production renders.

## Non-responsibility

No new renderer architecture, COLOR transform, cache policy, persistence, generic placement contract, or ocular solver is introduced.

## Consumers

`build_human_face()` and the production face registry/renderer are real production consumers.

## Guarantees

- default eye/ear center alignment is exact;
- nose bridge starts below eye-center level;
- nose/mouth gap has a non-zero aesthetic minimum;
- hair no longer uses a flat cap-like lower contour;
- existing shape/color/detail parameters remain renderable.
