# Pupil component truth

Identity: `CMP-EYE-PUPIL`.
Semantic parent: `CMP-EYE-IRIS` (Iris).
Aggregate/public parent: `CMP-EYE`.
Children: `PupilGlowSpec`, `PupilSmokeSpec` (value specifications; unchanged in V1.82).
Owner: `src/visual_engine/components/face/eyes/pupil/spec.py:9-31` for the canonical PupilSpec.

Responsibility: validate immutable local pupil specification values before aggregate/geometry consumption.
Non-responsibility: pupil geometry, gaze, iris containment, eyelid exposure, renderer serialization,
cache lifetime, database schema, generic COLOR resolution.

V1.82 correction: the owner now rejects bool/non-Real numeric inputs and includes `outline_width`
in the finite-state check. This closes a reproduced malformed-state boundary without changing valid values.

Status: `IMPLEMENTED / INTEGRATED / V1.82 HARDENED`.
