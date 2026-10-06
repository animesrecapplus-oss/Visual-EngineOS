# V1.84 — horizontal micro-component selection and audit

## VERIFY

Baseline: certified V1.83. The V1.83 roadmap explicitly requires a fresh horizontal audit before any Iris
implementation. `IrisSpec` has a real executable owner and real consumers; this is verified from source, not from
the blueprint alone.

## Candidate matrix

| Candidate | Owner evidence | Consumer evidence | Local contract/invariant evidence | Decision |
|---|---|---|---|---|
| Hair structural children | no independent executable owner | none independently | planning only | DEFER |
| Hair depth | existing owner | real | real | DEFER: no newly justified defect |
| Nose | existing owner | real | recent dossier | EXCLUDE: recent scope |
| Mouth | existing owner | real | recent dossier | EXCLUDE: recent scope |
| Ear | existing owner | real | recent dossier | EXCLUDE: recent scope |
| Iris | `face/eyes/iris/spec.py:8-41` | appearance, styles, generator, renderer, exports | real type annotations + runtime numeric checks, but hostile gaps reproduced | **SELECT** |

## Selection reason

`IrisSpec` is the smallest already-executable eye value boundary that is directly upstream of the now-corrected
`IRIS → PUPIL` semantic relation. The renderer consumes `ring_count` and `pattern_count` through `range(...)`, while
`outline_width` is used arithmetically. The existing constructor allowed fractional/bool count values and non-finite
`outline_width`; this is a concrete local validation defect, not a speculative feature request.

## Scope

One owner and one responsibility:

`src/visual_engine/components/face/eyes/iris/spec.py` — local IrisSpec numeric/type boundary hardening.

No geometry, gaze, pupil containment, eyelid exposure, highlight, COLOR, cache algorithm, database or renderer logic
is changed by V1.84.

## Status boundary

This audit does not promote deeper Iris morphology atoms such as fibres, crypts, pigmentation, transmission or
cornea attachment. Those remain separate future ownership questions requiring their own executable evidence.
