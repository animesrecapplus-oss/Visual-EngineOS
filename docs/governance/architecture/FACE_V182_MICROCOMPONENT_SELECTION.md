# V1.82 — micro-component selection and audit

## VERIFY result

Checkpoint: certified V1.81. The checkpoint ZIP hash is recorded in the V1.82 certification.
The archive contains no Git metadata, so Git cleanliness cannot be claimed from the checkpoint.
It also contains a `.pytest_cache` directory despite the V1.81 certification claiming generated
cache purge; this is recorded as a checkpoint hygiene discrepancy, not silently treated as clean.

V1.81 Mouth is excluded. V1.80 Ear and V1.79 Nose are excluded by horizontal progression.
Hair structural children remain PLANNED and have no executable owners.

## Candidate matrix

| Candidate | Owner | Real consumers | Contract/invariants | Selection |
|---|---|---|---|---|
| Hair children | none | none independently | planning only | DEFER |
| Ear | existing | real | real | EXCLUDE: V1.80 |
| Mouth | existing | real | real | EXCLUDE: V1.81 |
| Nose | existing | real | dossier completed V1.79 | EXCLUDE: recent scope |
| Hair depth | `face/hair.py:54-56` | real | real | DEFER: no justified defect |
| Pupil | `face/eyes/pupil/spec.py:8-29` | real | real | SELECT |

## Selection

`CMP-EYE-PUPIL` is selected because it is a real executable specification micro-component with
real production consumers, a parent/child boundary, existing contracts/invariants, cache impact
mapping, hostile tests and public compatibility exports. The audit reproduced a concrete local
validation defect before implementation.

Scope is one owner and one responsibility: `PupilSpec` local numeric-state validation.
