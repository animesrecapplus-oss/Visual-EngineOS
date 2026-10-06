# Iris impact map — V1.84

`IMP-IRIS-001` — direct source impact is limited to `iris/spec.py`; the new focused tests are the only test-source
addition.

`IMP-IRIS-002` — real consumers include EyeAppearance, styles, generator/cache projection, SVG renderer, paired-eye
colour replacement and compatibility exports. Their valid-input behaviour must remain unchanged.

`IMP-IRIS-003` — parent/child impact is semantic only: Iris remains under the eyeball branch and remains the semantic
parent of Pupil. No hierarchy runtime code changes.

`IMP-IRIS-004` — cache/fingerprint: `iris_shape` remains the only Iris field in `_eye_cache_inputs`; V1.84 does not
add visual-only fields to geometry identity.

`IMP-IRIS-005` — provenance: no new provenance field or transformation exists in this owner.

`IMP-IRIS-006` — persistence/database: source audit found no IrisSpec database adapter or migration. No DB change.

`IMP-IRIS-007` — determinism: valid constructor output remains deterministic and immutable; invalid states now fail
before downstream execution.

`IMP-IRIS-008` — visual: valid renders must remain identical. Hostile invalid values are rejected before rendering.

`IMP-IRIS-009` — COLOR: no COLOR implementation or contract changes are justified by this local boundary defect.

`IMP-IRIS-010` — if a new fact appears, this impact map must be reopened before further modification.

`IMP-IRIS-011` — certification-state impact: implementation and evidence can be validated, but repository cleanliness
cannot be certified without `.git` metadata. Final status must remain BLOCKED rather than PASS.
