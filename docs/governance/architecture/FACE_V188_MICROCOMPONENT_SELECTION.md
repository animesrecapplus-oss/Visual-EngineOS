# V1.88 — horizontal micro-component selection and pre-change audit

## VERIFY

Baseline is the exact V1.87 certified package. Its ZIP SHA-256 is
`fe85b5465824336153ca2baf5eedbe6eae215edaaa25f14243a97d2c7995fba6`; the extracted source is therefore the
certified V1.87 code before this brick. V1.87 certification records 209 modules, 567 edges, 3 pre-existing SCCs,
0 new SCCs, 0 duplicate groups, 8 unchanged DB migrations, 1443 collected tests / 1442 pass / 1 expected
PostgreSQL skip / 0 fail, and Git NOT_APPLICABLE.

Fresh local probes were executed against the extracted V1.87 code. `ReflectionMark` accepts numeric strings and
booleans in numeric fields, can leak `OverflowError` for huge integers, and accepts an unknown `shape` value.
The unknown shape is not harmless: the renderer's final branch renders every non-circle/non-ellipse/non-diamond
shape as a streak/rect path. This is a concrete local input-boundary defect with a verified executable owner.

## Fresh candidate matrix

| Candidate | Owner | Real consumers | Current defect probe | Decision |
|---|---|---|---|---|
| Eyelid | `eyelid/spec.py` | appearance/generator/render | V1.86 hardened | DEFER |
| Lash | `lashes/spec.py` | appearance/render | V1.85 hardened | DEFER |
| Iris | `iris/spec.py` | appearance/styles/generator/render | V1.84 hardened | DEFER |
| Pupil | `pupil/spec.py` | appearance/styles/generator/render | V1.82 hardened | DEFER |
| Eyebrow | `eyebrow/spec.py` | appearance/styles/expression/render/API | V1.87 hardened | DEFER |
| Highlight | `highlights/spec.py` | appearance/styles/render/visibility/API export | permissive numeric types + open shape vocabulary | **SELECT** |
| Eye visibility | `visibility.py` | appearance/render/API | strict bool + closed node map already present | DEFER |
| Hair structural atoms | no independent executable owner | none independently verified | no owner | DEFER |
| Mouth/nose/ear subregions | no new executable micro-owner | none independently verified | no new boundary | DEFER |

## IDENTIFY

Component: `CMP-EYE-HIGHLIGHT`; symbol `ReflectionMark`; canonical owner
`src/visual_engine/components/face/eyes/highlights/spec.py:6-23` (VERIFIED).
Aggregate parent: `CMP-EYE` (VERIFIED). Semantic classification: cross-relation ocular reflection/highlight system,
not a fixed Pupil child (VERIFIED by the V1.83 hierarchy matrix). Direct consumers verified in
`appearance/spec.py`, `styles.py`, `eye_svg_effects.py`, `definitions.py` and `geometry/__init__.py`.

No semantic child is promoted by this brick. Siblings are other periocular/ocular systems; no new sibling relation
is introduced. Persistence and DB ownership are UNKNOWN until impact inspection; no change is authorized by default.

## ARCHITECT / SCOPE

Responsibility: validate immutable local `ReflectionMark` authored input before downstream use.
Non-responsibility: highlight placement solver, optical physics, iris geometry, visibility hierarchy, renderer
orchestration, COLOR transformation, cache policy, persistence, or new highlight anatomy.

Input boundary: typed shape vocabulary, non-bool finite real geometry/opacity/rotation values, valid hex color.
Output boundary: immutable `ReflectionMark` value object with the same valid authored values; no coercion.
Authority: only local validation and existing value-object fields. Mutation: none after construction.
Lifecycle: construction → appearance/style/render use → object destruction; no persistence lifecycle identified.

Authorized change: one runtime owner (`highlights/spec.py`), focused adversarial tests, truth dossier, governance
records, verification/visual evidence. No shared `_finite` change and no renderer algorithm change.
