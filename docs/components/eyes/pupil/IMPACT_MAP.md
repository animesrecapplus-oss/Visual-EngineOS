# Pupil impact map — V1.82

## Direct

`pupil/spec.py:24-31` affects PupilSpec construction and therefore its real aggregate/style/generator consumers.

## Relational

No changes to Iris, Gaze, Eyelid, Transform, Lashes, Pupil effects or EyePair ownership.

## Cache/fingerprint

`eyes/generator.py:192-226` includes geometry-affecting pupil values. V1.82 does not change the selected cache fields,
cache lifetime or fingerprint algorithm. Invalid states now fail before a valid request can enter this path.

## Persistence/database

No PupilSpec database representation or migration exists in the verified production path; no DB change is authorized.

## Visual

Valid geometry and appearance must remain unchanged. Hostile values are rejected before rendering.

## Required acceptance

Component tests → consumers → parent/relations → production path → cache identity → full regression → visual invariance.
