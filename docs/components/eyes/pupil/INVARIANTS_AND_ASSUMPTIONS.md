# Pupil invariants and assumptions

## Invariants

- `INV-PUPIL-001`: every PupilSpec numeric field is Real and finite; bool is not accepted as numeric state.
- `INV-PUPIL-002`: scale fields are strictly positive; outline width is finite and non-negative.
- `INV-PUPIL-003`: opacity is finite and within `[0,1]`.
- `INV-PUPIL-004`: authored pupil and outline colours pass the shared validator.
- `INV-PUPIL-005`: PupilSpec remains immutable.
- `INV-PUPIL-006`: valid authored values are not coerced or rewritten by V1.82.

## Assumptions

- downstream geometry consumes validated PupilSpec values;
- cache inputs include geometry-affecting pupil fields already selected by the Eye owner;
- interaction relations remain owned by their respective components.

## Boundary

V1.82 does not certify containment, gaze, eyelid exposure or camera-transform semantics.
