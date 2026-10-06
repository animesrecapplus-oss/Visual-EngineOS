# V1.87 — horizontal micro-component selection and audit

## VERIFY

Baseline: V1.86 certified `CMP-EYE-EYELID` local input hardening. Git is explicitly out of scope because the project
is not a Git repository. The V1.86 certified release was reopened and checked against its source identity, tests,
dependency graph, database identity, visual evidence and current artifacts before selecting a new brick.

## Fresh candidate matrix

| Candidate | Owner | Real consumers | Existing evidence | Local defect probe | Decision |
|---|---|---|---|---|---|
| Eyelid | `eyelid/spec.py` | appearance/generator/render | V1.86 dossier | already hardened | DEFER |
| Lash | `lashes/spec.py` | appearance/render | V1.85 dossier | already hardened | DEFER |
| Iris | `iris/spec.py` | appearance/styles/generator/render | V1.84 dossier | already hardened | DEFER |
| Pupil | `pupil/spec.py` | appearance/styles/generator/render | V1.82 dossier | already hardened | DEFER |
| Eyebrow | `eyebrow/spec.py` | appearance/styles/expression/render/API | executable owner + hierarchy evidence | non-finite/type permissiveness reproduced | **SELECT** |
| Highlight | `highlights/spec.py` | appearance/styles/render | finite numeric validation | no stronger local defect reproduced | DEFER |
| Eye visibility | `visibility.py` | appearance/render/API | explicit hierarchy contract | no stronger local input defect | DEFER |
| Hair structural atoms | no independent executable owner | none independently verified | planned | no executable owner | DEFER |
| Mouth/nose/ear subregions | no new owner | none independently verified | recent scopes/planning | no new executable boundary selected | DEFER |

## Selection reason

`BrowSpec` is a verified executable micro-component under `ORBIT / PERIOCULAR`. Its owner is real and directly
consumed by appearance, styles, expression, SVG rendering and the compatibility geometry export. A fresh probe
reproduced a concrete local boundary defect: `length`, `thickness`, `angle_deg`, `x` and `y` accept non-finite values;
`enabled` accepts non-bools; numeric strings are accepted by untyped fields; very large integers can escape local
validation and `min_eye_gap`/`max_eye_gap` can raise `OverflowError` during `math.isfinite` instead of being rejected
as invalid input.

## Scope

One canonical owner: `src/visual_engine/components/face/eyes/eyebrow/spec.py`.

One responsibility: harden `BrowSpec` local boolean/type/finiteness input validation while preserving existing numeric
ranges, style vocabulary, color validation, placement semantics, hierarchy/rotation inheritance, geometry cache
identity, visibility, COLOR, persistence and renderer behavior.
