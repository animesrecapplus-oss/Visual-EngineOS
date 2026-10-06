# V1.86 — horizontal micro-component selection and audit

## VERIFY

Baseline: V1.85 certified Lash input-boundary hardening. Git remains explicitly out of scope because the project is
not a Git repository. The baseline was re-opened from the V1.85 release and checked against source, tests, artifacts,
dependency/database evidence and the V1.85 checkpoint.

## Fresh candidate matrix

| Candidate | Owner | Consumers | Contract/invariant evidence | Reproduced defect | Decision |
|---|---|---|---|---|---|
| Lash | `lashes/spec.py` | renderer/appearance | V1.85 dossier | already hardened | DEFER |
| Iris | `iris/spec.py` | appearance/styles/generator | V1.84 dossier | already hardened | DEFER |
| Pupil | `pupil/spec.py` | appearance/styles/generator | V1.82 dossier | already hardened | DEFER |
| Eyelid | `eyelid/spec.py` | appearance/generator/render | existing range/type annotations | bool and non-finite gaps reproduced | **SELECT** |
| Eyebrow | `eyebrow/spec.py` | appearance/styles/expression/render | executable owner | broader placement/type boundary; no stronger local defect selected | DEFER |
| Highlight | `highlights/spec.py` | appearance/styles/generator | finite numeric validation | no stronger local defect | DEFER |
| Hair structural atoms | none | none independently | planning only | none | DEFER |
| Oral/nasal/ear subregions | no new owner | none independently | recent scopes/planning | none | DEFER |

## Selection reason

`EyelidAppearance` is a real executable value owner with direct production consumers. Its existing range checks define
valid numeric domains but do not reject booleans or non-finite values consistently. Reproduction before modification
showed `NaN`/infinity accepted for width/offset/crease-width fields and integer/string values accepted for boolean
controls. The renderer and geometry cache already have explicit ownership boundaries, so local validation can close
this defect without inventing a new geometry component.

## Scope

One canonical owner: `src/visual_engine/components/face/eyes/eyelid/spec.py`.

One responsibility: harden local `EyelidAppearance` input types and finiteness while preserving all existing ranges,
colors, styles, geometry, cache identity, visibility, COLOR, persistence and rendering behavior.
