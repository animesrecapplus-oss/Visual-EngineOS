# Current status — V1.83

## V1.83 — Eye semantic hierarchy / ownership correction

V1.83 reopened the V1.82 impact analysis after a concrete architecture fact was identified: the V1.82 Pupil dossier
used `CMP-EYE` as its parent, but existing ocular contracts explicitly define Pupil as an Iris child. `CMP-EYE` is
retained as the aggregate/public eye-system owner.

The corrected hierarchy is `FACE → ORBIT/PERIOCULAR → EYEBALL → IRIS → PUPIL`, with eyelid, lashes and eyebrow as
related periocular branches and gaze/highlight/occlusion/transform as cross-relations. The envelope is a renderer-neutral
measurement layer, not an anatomical layer. Blueprint atoms remain distinct from executable micro-components.

No runtime source, database, cache identity, COLOR algorithm or rendering semantics changed. V1.83 is accepted only
as an architecture/documentation correction after truth validation, hostile documentation checks, regression,
compileall, dependency/cycle review and artifact cleanup.
