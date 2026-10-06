# V1.89 — horizontal micro-component selection and pre-change audit

## VERIFY

Baseline is the exact V1.88 certified package. ZIP SHA-256:
`b8ea6fdab743097d5d2740942f5e9c0f5fe26cdc58347168f05f5ed67544486e`.
The package contains 209 Python source modules and V1.88 certification records 1500 collected tests /
1499 pass / 1 expected PostgreSQL skip / 0 fail, 209 modules / 567 edges, 3 pre-existing SCCs,
0 new SCCs, 0 duplicate groups and 8 unchanged DB migrations.

The project is not a Git repository; Git is `NOT_APPLICABLE`, not a gate.
The root README still says V1.77 is the current production frontier. This is stale documentation,
not a current checkpoint: the V1.88 certification artifact and V1.88 current-status record agree on V1.88.
The README discrepancy is recorded as `CONFLICTING` documentation metadata and does not alter the executable baseline.

Fresh probes against the exact V1.88 source found a concrete Gaze input-boundary defect:
`Gaze(x="0.5")`, `Gaze(x=True)` and `Gaze(target=("0", 0))` are accepted; a huge integer can leak
`OverflowError`; a mutable list target is accepted despite the declared tuple boundary. Downstream `vector()`
or `gaze_to_local()` can then fail after the object has crossed its constructor boundary.

## Fresh candidate matrix

| Candidate | Owner | Real consumers | Fresh probe | Decision |
|---|---|---|---|---|
| Eyelid | `eyelid/spec.py` | appearance/generator/render | V1.86 hardened | DEFER |
| Lash | `lashes/spec.py` | appearance/render | V1.85 hardened | DEFER |
| Iris | `iris/spec.py` | appearance/styles/generator/render | V1.84 hardened | DEFER |
| Pupil | `pupil/spec.py` | appearance/styles/generator/render | V1.82 hardened | DEFER |
| Eyebrow | `eyebrow/spec.py` | appearance/styles/expression/render/API | V1.87 hardened | DEFER |
| Highlight | `highlights/spec.py` | appearance/styles/render/API | V1.88 hardened | DEFER |
| Eye visibility | `visibility.py` | appearance/render/API | strict bool + closed node map | DEFER |
| Gaze | `gaze/solver.py` | geometry builder/generator/pair/transform/public exports | permissive authored types + overflow | **SELECT** |
| OcularPose3D | `geometry/view_axis.py` | spherical/alignment/runtime transform | finite check exists; weaker local defect | DEFER |
| Caruncle | `appearance/caruncle.py` | appearance/builder/renderer/cache | bool enable permissiveness; separate leaf scope | DEFER |
| Pupil effects | `pupil/effects.py` | PupilSpec/API only; no renderer consumer proven | permissive effect controls | DEFER: no stronger independent production consumer |
| Hair structural atoms | no independent executable owner | none independently verified | no owner | DEFER |
| New mouth/nose/ear subregions | no new executable micro-owner | none independently verified | no new boundary | DEFER |

## IDENTIFY

Selected component: `CMP-EYE-GAZE`; selected symbol: `Gaze`; canonical owner
`src/visual_engine/components/face/eyes/gaze/solver.py:26-52` (VERIFIED).

Semantic classification: ocular cross-relation system controlling internal ocular assembly; it is not a
fixed child of Pupil and not a renderer layer (VERIFIED by the V1.83 hierarchy matrix and existing gaze contracts).
Aggregate/public parent: `CMP-EYE` (VERIFIED). Semantic frame: EYEBALL / ocular assembly (VERIFIED).

Direct consumers verified: `geometry/builder.py`, `geometry/transform.py`, `generator.py`, `pair.py`,
`geometry_builder.py`, compatibility exports in `definitions.py` and `geometry/__init__.py`.
Indirect production relation: EyeGeometry generation and SVG production through the existing eye production path.

No Gaze solver algorithm, 3D optical model, prompt parser, renderer algorithm, cache policy, COLOR semantics,
or persistence is selected by this brick.

## ARCHITECT / SCOPE

Responsibility: validate the immutable authored `Gaze` value-object boundary before downstream arithmetic.
Non-responsibility: gaze solving, aperture intersection, binocular convergence, 3D depth, prompt semantics,
transform policy, renderer orchestration, cache policy, COLOR, database/persistence.

Input boundary: `x/y/strength/amplitude` finite non-bool `Real`; `direction` closed runtime vocabulary;
`target` either `None` or an immutable 2-tuple of two finite non-bool `Real` values.
Output boundary: same authored values, no coercion, immutable `Gaze` object.
Authority: local validation only. Mutation: none after construction.
Lifecycle: construction → transform/solver/generator use → object destruction; no persistence lifecycle identified.

Authorized runtime change: one owner module (`gaze/solver.py`), focused tests, truth dossier, governance and evidence.
The shared `_finite` helper is retained because `BinocularGazeSolver` still consumes it; only the authored `Gaze` constructor boundary is hardened locally. `gaze/semantics.py` is not changed.
