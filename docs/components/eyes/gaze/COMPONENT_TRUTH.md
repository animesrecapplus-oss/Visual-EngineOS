# Component truth — CMP-EYE-GAZE

## Identity
`Gaze` is an immutable request/value object for eye-local or explicit scene-target gaze.

## Responsibility
Validate the authored constructor boundary: finite numeric offsets/magnitudes, closed direction vocabulary,
and an immutable finite numeric target pair.

## Non-responsibility
`GazeSolver`, binocular convergence, aperture intersection, pupil containment policy, 3D depth projection,
prompt parsing, rendering, visibility, cache lifetime, COLOR, database persistence.

## Authority
The owner controls only `Gaze` field validity. It does not alter authored values and does not resolve them.

## Inputs / outputs
Inputs are the fields declared by `Gaze`; valid values are retained without coercion. Output is a frozen/slots
`Gaze` object consumed by existing solver/transform/generator paths.

## Lifecycle
Construction → geometry/transform/pair use → destruction. No persistence lifecycle is identified.

## Guarantees
Only the V1.89 local input-boundary guarantees in `CONTRACTS.md` and `GUARANTEES_AND_STATUS.md` are certified.

## File identity
`FILE-GAZE-001` = runtime owner; `FILE-GAZE-002` = focused test file. Exact final hashes and ranges are recorded in V1.89 evidence.
