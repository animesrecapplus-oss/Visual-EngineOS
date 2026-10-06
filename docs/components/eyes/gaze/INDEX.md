# CMP-EYE-GAZE — V1.89 truth dossier

Status: CERTIFIED for the documented local `Gaze` authored-input boundary only.

- Identity: immutable ocular gaze request value object.
- Owner: `src/visual_engine/components/face/eyes/gaze/solver.py:26-71`, V1.89.
- Parent: semantic EYEBALL / ocular assembly; aggregate `CMP-EYE`.
- Responsibility: reject malformed authored gaze values before downstream arithmetic.
- Non-responsibility: gaze solving algorithm, 3D optics, prompt intent, renderer, cache policy, COLOR, DB.
- Consumers: geometry builder, generator, pair solver path, gaze transform, public compatibility exports.
- Contracts: `CON-GAZE-001..007`.
- Invariants: `INV-GAZE-001..007`.
- Tests: `TST-GAZE-001..006`.
- Adversarial tests: `ADV-GAZE-001..010`.
- Relations: `REL-GAZE-001..008`.
- Decisions: `DEC-GAZE-001..005`.
- Errors: `ERR-GAZE-001..004`.
- Impacts: `IMP-GAZE-001..011`.
- Evidence: `EVD-GAZE-001..010`.

No broader gaze-behaviour or optical-quality guarantee is promoted.
