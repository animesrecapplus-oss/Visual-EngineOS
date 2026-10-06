# Pupil component dossier — V1.82

Identity: `CMP-EYE-PUPIL`.
Semantic path: `face/eyes/pupil`.
Semantic parent: `CMP-EYE-IRIS` (Iris).
Aggregate/public parent: `CMP-EYE`.
Canonical owners: `pupil/spec.py` and `pupil/effects.py` for their respective value specifications.

V1.82 scope: harden `PupilSpec` local numeric validation only.

Truth files: COMPONENT_TRUTH, CONTRACTS, DEPENDENCIES_AND_CONSUMERS, INVARIANTS_AND_ASSUMPTIONS,
ADVERSARIAL_TEST_MATRIX, RELATIONS, DECISIONS, ERRORS, IMPACT_MAP, EVIDENCE, GUARANTEES_AND_STATUS,
ROADMAP, TEST_STATUS and MANIFEST.

Source owner line range: `src/visual_engine/components/face/eyes/pupil/spec.py:9-31`.
Test line range: `tests/components/face/eyes/pupil/test_v182_pupil_input_hardening.py:1-30`.

Status: `CERTIFIED` only after the complete V1.82 gate. Interaction items outside this owner remain DECLARED.

V1.83 hierarchy correction: the previous `CMP-EYE` parent label was an aggregate-parent shorthand. It is not the direct semantic parent. Existing V1.15/V1.17 ocular contracts explicitly keep Pupil as an Iris child. No runtime ownership or rendering semantics changed.
