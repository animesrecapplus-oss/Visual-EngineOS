# V1.85 — horizontal micro-component selection and audit

## VERIFY

Baseline is the V1.84 implementation/validation checkpoint. Git is intentionally out of scope for this project;
repository certification is not a project prerequisite for this brick. V1.84 evidence, source tree, tests, artifacts,
database identity and dependency graph are the working baseline.

## Fresh candidate matrix

| Candidate | Executable owner | Real consumers | Contract/invariant evidence | Current defect evidence | Decision |
|---|---|---|---|---|---|
| Hair structural children | none | none independently | planning only | none | DEFER |
| Hair depth | no standalone source owner proven | renderer/relation path documented | existing dossier/history | no newly justified defect | DEFER |
| Nose | `generators.py` | face composites | recent dossier | recent scope | EXCLUDE |
| Mouth | `components/face/mouth.py` | face composites | recent dossier | recent scope | EXCLUDE |
| Ear | `components/face/ear.py` | ear composite | recent dossier | recent scope | EXCLUDE |
| Iris | `iris/spec.py` | appearance/styles/generator/renderer | V1.84 dossier | V1.84 already addressed | DEFER |
| Pupil | `pupil/spec.py` | appearance/styles/generator/exports | V1.82 dossier | V1.82 already addressed | DEFER |
| Eyelid | `eyelid/spec.py` | appearance/generator/render path | executable checks exist | no isolated reproduced defect selected over Lash | DEFER |
| **Lash** | `lashes/spec.py` | appearance, styles/profiles, renderer, public exports | executable local checks | fractional/bool count and non-finite/overflow numeric gaps reproduced | **SELECT** |
| Eyebrow | `eyebrow/spec.py` | appearance/styles/expression/renderer | executable checks exist | broader untyped placement boundary, but larger scope | DEFER |
| Highlight | `highlights/spec.py` | appearance/styles/generator/exports | finite numeric checks exist | no stronger local defect | DEFER |

## Selection reason

`LashSpec` and `LowerLashSpec` are one existing executable lash value boundary with two directly related value
classes. The renderer calls `range(lashes.count)`, so fractional count is an immediate type/contract defect; bool is
also accepted as an integer-like value. Several float fields accept `+/-inf` or `NaN` because only relational bounds
are checked. These states are reproducibly accepted before modification.

## Scope

One canonical owner: `src/visual_engine/components/face/eyes/lashes/spec.py`.

One responsibility: harden local LashSpec/LowerLashSpec numeric input validation without changing lash geometry,
rendering algorithms, style vocabulary, effects ownership, cache behavior, COLOR, persistence or public compatibility.

## Result

V1.85 implementation remained within the selected owner. Focused hostile tests and full integration passed. Valid
production rendering is byte-identical to V1.84 across the audited cases. The micro-component is now `CERTIFIED` for
this narrow input-boundary scope.
