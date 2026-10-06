# Errors — CMP-FACE-EYE-BILATERAL

- `ERR-FEB-001`: V1.90 confirmed HumanFace production left Eye reached the Eye generator with `side="single"` and therefore reversed medial/lateral canthus semantics.
- `ERR-FEB-002`: an unused `_eye_component_inputs()` helper in `face/generators.py` represented the same stale boundary and was not a real runtime consumer.
- `ERR-FEB-003`: initial V1.91 focused test assumption incorrectly expected a standalone positive-x `right_eye` ID to mirror; the test was corrected after observing the existing `single` contract. No runtime code was changed for this test correction.

No new runtime error class is introduced.
