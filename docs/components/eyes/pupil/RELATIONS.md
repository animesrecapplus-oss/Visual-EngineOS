# Pupil relations

`REL-PUPIL-PARENT` — semantic parent is `CMP-EYE-IRIS`; aggregate/public owner is `CMP-EYE`, which stores and assembles the pupil value. This is not a linear Eye→Pupil semantic chain.

`REL-PUPIL-EFFECTS` — `PupilGlowSpec` and `PupilSmokeSpec` are child value specifications owned by the pupil package;
V1.82 does not change them.

`REL-PUPIL-IRIS` — pupil relative placement/containment is downstream geometry ownership; status `DECLARED` here.

`REL-PUPIL-GAZE` — gaze moves the resolved ocular assembly; status `DECLARED` here.

`REL-PUPIL-EYELID` — eyelid exposure/occlusion is a downstream relation; status `DECLARED` here.

`REL-PUPIL-TRANSFORM` — local-to-camera transform is owned by ocular transform infrastructure; status `DECLARED` here.

`REL-PUPIL-RENDER` — renderer consumes resolved geometry, not raw PupilSpec semantics; status `INTEGRATED`.

`REL-PUPIL-LASH` — LashShadowSpec ownership correction remains resolved in `lashes/effects.py`.

`REL-PUPIL-HIERARCHY-CORRECTION` — V1.83 separates semantic parentage from aggregate ownership. Existing V1.15/V1.17 contracts establish Iris → Pupil attachment. Status: `DOCUMENTED / NO RUNTIME CHANGE`.
