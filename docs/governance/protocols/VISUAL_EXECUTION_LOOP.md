# Visual execution loop — V1.50

## Canonical loop

`PROMPT → PARAMETERS → PERSISTENCE → RESOLUTION → CODE → EXECUTION → FRAME/IMAGE/VIDEO → INSPECTION → DIAGNOSIS → CORRECTION → TEST → NEW EXECUTION`

The loop is mandatory whenever a change can affect rendered output.

## Traceability

The run must identify prompt/input provenance, parameter snapshot, database/version identity where applicable,
engine version, component IDs, relevant contracts, deterministic seed, output fingerprint and evidence location.

## Inspection levels

**Normal:** expected representative state.

**Boundary:** minimum/maximum, zero/non-zero, extreme orientation, extreme exposure or equivalent domain edge.

**Interaction:** neighbouring component, parent/child, occluder, camera or style context likely to expose coupling.

## Diagnosis rule

A visual defect is not fixed by a renderer patch unless the renderer owns the defect. Diagnose backward through
geometry, component contract, resolved parameters and source provenance. Record the root cause and the contract/invariant changed.

## Acceptance

Numerical tests, deterministic hashes and visual inspection answer different questions. None substitutes for another
when that evidence class is applicable.

## No-artifact rule

Generated evidence is disposable. Keep only the current brick evidence in `artifacts/current/vX.Y/`; put durable conclusions,
parameters, defects and decisions into bounded documentation. Superseded generated evidence is purged before certification.
