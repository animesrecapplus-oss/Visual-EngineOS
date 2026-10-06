# Pupil contracts

`CON-PUPIL-001` — all numeric PupilSpec fields are real numeric values and finite. Bool/string coercion is rejected.

`CON-PUPIL-002` — `scale`, `scale_x`, `scale_y` are strictly positive; `outline_width` is finite and non-negative.

`CON-PUPIL-003` — opacity is finite and bounded to `[0,1]`; effect bounds remain owned by their effect specs.

`CON-PUPIL-004` — pupil and outline colours use the shared eye colour validator.

`CON-PUPIL-005` — PupilSpec is an immutable frozen value object.

V1.82 enforcement owner: `pupil/spec.py:24-31`.

No contract is promoted for pupil/iris containment, gaze displacement, eyelid exposure or transform behavior;
those relations remain downstream ownership boundaries.
