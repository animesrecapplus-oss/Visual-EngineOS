# Eyes component family

This package owns the face-eye system and remains the reference component for deep engine development.

## Current implementation ownership

- `core.py`: compatibility facade for the public ocular API.
- `definitions.py`: compatibility facade only; no domain implementation.
- `geometry_builder.py`: compatibility facade only; implementation is split under `geometry/`.
- `pair.py`: bilateral eye-pair construction and constraints.
- `expression.py`: current authoring-level ocular expression modifiers.
- `profiles.py`: presentation/age visual profiles.
- `styles.py`: reference-oriented appearance presets.
- `generator.py`: renderer-neutral geometry-generator bridge and cache projection.
- `pupil/`, `iris/`, `eyelid/`, `lashes/`, `eyebrow/`, `highlights/`, `effects/`: public subpackage boundaries for
  future deeper domain implementations.

## V1.4 deepening plan

The remaining eye work is decomposed into 284 atomic/subatomic tasks across 17 streams. See:

- `docs/components/eyes/blueprint/V1.4_EYE_ATOMIC_BLUEPRINT__part_01.md` — human-readable decomposition and relationships.
- `docs/components/eyes/blueprint/index.json` — stable machine-readable task inventory.
- `docs/components/eyes/blueprint/V1.4_EYE_EXECUTION_PROTOCOL.md` — mandatory implementation/test/artefact/visual/correction/validation cycle.

The subpackages are stable ownership boundaries. New deep logic should be placed behind the relevant boundary rather than
reintroduced into compatibility facades or duplicated in the renderer.

## Structural rule — no fourre-tout

V1.4 treats module ownership as part of correctness, not cosmetic cleanup. Focused eye implementation files are budgeted at **250 lines maximum**; compatibility facades are exempt only because they contain re-exports, not implementation. A domain is split again when a file starts mixing independent responsibilities rather than waiting for it to become a monolith.

Current geometry ownership:

- `geometry/shape.py` — shape factors and local rotation/clamping primitives.
- `geometry/curve.py` — Bézier/curve sampling and offsets.
- `geometry/contour.py` — aperture contour construction and bounds.
- `geometry/containment.py` — radial/iris containment helpers.
- `geometry/lid_follow.py` — bounded gaze-follow deformation.
- `geometry/builder.py` — final eye and binocular assembly only.

Current definition ownership:

- `contracts/` — shared eye types and validation primitives.
- `morphology/` — intrinsic eye morphology parameters.
- `pupil/` — pupil and pupil-effect specifications.
- `iris/` — iris specification.
- `eyelid/` — eyelid appearance contract.
- `lashes/` — upper/lower lash specifications.
- `eyebrow/` — brow specification.
- `highlights/` — structured reflection/highlight marks.
- `appearance/` — aggregate appearance contract and contour contract.
- `gaze/` — gaze and binocular gaze solvers.

## V1.10 orientation and reference boundary

- `EyeParameters.rotation_deg` is the screen-plane ocular roll.
- `EyeParameters.alignment_axis_rotation_deg` is the independent depth rotation about the local interocular/alignment X axis, projected as foreshortening by the current 2D backend.
- `geometry/orientation.py` owns the transform math; `geometry/internal.py` applies the same projection to iris/pupil/reflection children.
- `gaze/semantics.py` owns stable prompt-facing ocular intent names. Depth intents such as `look_behind_right_eye` are explicit and are not guessed into a 2D screen direction.
- `reference/pixel_trace.py` and `reference/overlay.py` keep source-pixel digitization human-gated and renderer-neutral.

## V1.11 pixel calibration boundary

`reference/review.py` owns the explicit candidate-review state machine. `reference/calibration.py`
owns terminal semantics and source-pixel measurements. `reference/pixel_trace.py` owns dense,
orientation-independent trace proposals. `reference/overlay.py` owns fixed reference↔engine comparison.

The 28-candidate review queue is deliberately not equivalent to 28 approved eyes: the supplied sheet
contains both individual eye studies and contextual face panels. Human approval is required before a
candidate becomes `ReferenceSample` geometry. Real overlays and MOR promotion are therefore blocked
until explicit approvals exist.

## V1.13 — spherical ocular view layer

V1.13 adds an explicit spherical globe/view-axis layer without replacing the existing
2D eyelid aperture. `EyeParameters.ocular_yaw_deg` and `ocular_pitch_deg` control the
view axis; `rotation_deg` remains roll and `alignment_axis_rotation_deg` remains the
interocular-axis rotation. The globe/iris/pupil/cornea are projected from 3D geometry
and then clipped by the independent eyelid aperture. This is a geometric 3D surface
model, not yet a complete anatomical/optical eyeball.
