# Pupil guarantees and status

## Guarantees

1. Invalid local numeric state fails at PupilSpec construction.
2. `outline_width` cannot be NaN or infinite.
3. bools and coercive strings cannot masquerade as numeric PupilSpec state.
4. Valid PupilSpec values retain their authored numeric values.
5. PupilSpec remains immutable.
6. No V1.82 change is made to pupil geometry, renderer, COLOR, database or cache algorithm.

## Status

`IMPLEMENTED`: local PupilSpec validation.
`INTEGRATED`: EyeAppearance, style, generator and compatibility consumers remain exercised.
`VISUAL_INVARIANCE`: valid production render output must remain identical to V1.81.
`DECLARED`: pupil/iris, pupil/gaze, pupil/eyelid and pupil/transform interaction ownership.
