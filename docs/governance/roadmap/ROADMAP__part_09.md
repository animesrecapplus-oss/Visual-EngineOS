<!-- Refactored from docs/governance/roadmap/ROADMAP__part_01.md; source lines 1073-1201; content preserved. -->
<!-- Part 9/16. Use the family index for navigation. -->
### 2026-09-17 — MOR CanthusMetrics measurement brick

Implemented the small measurement step after `EnvelopeMetrics`. The new canonical metric layer
quantifies canthus chord/arc transition length, local endpoint tangent angles, net versus absolute
turning, curvature peak/mean, endpoint curvature concentration, half-turn window, chord deviation,
and a non-normative triangular-closure evidence index. Primary arc-length and curvature integrals
use fixed 128-point Gauss-Legendre quadrature; distribution diagnostics use an explicit odd sample count and are
convergence-tested. Eight real eye families plus three synthetic calibration curves produce visible
SVG/PNG evidence. No reference threshold is invented: numeric anime calibration remains future work
requiring digitized reference curves and visual review.

### 2026-09-18 — MOR canthus reconstruction micro-brick

Implemented the first geometry-correction step after `CanthusMetrics`: the artificial fixed
0.2*half-height endpoint floor was removed. Zero/low roundness now resolves to a small numerical
floor while explicit roundness controls the actual canthus half-gap. Before/after SVG/PNG evidence,
33-point sampled diagnostics, magnified corner views and separated performance timings are generated.
The dense direct geometry challenge covers 9 eye shape families × 3 openings × 4 resolutions × 3
rotations × 4 gaze directions × 5 inner/outer roundness pairs = 6480 reconstructions, with full-contour
checks retained in the focused builder tests. Remaining tangent/curvature-profile mismatch is still open.

### 2026-09-18 — MOR canthus curvature-profile micro-brick

Implemented an opt-in continuous endpoint-transition axis for inner and outer canthi. The axis
changes the local tangent-handle construction upstream of the C1 cubic bridge rather than faking
extra cubic control points. `transition=0` is exactly compatible with V1.4. The sweep covers 6
contexts × 5 transition values and emits actual SVG/PNG renders plus 33-sample bridge overlays.

The numerical response is real: on the default almond calibration case, increasing transition from
0 to 1 reduced endpoint-curvature concentration from about 0.889 to 0.776 and curvature
peak-to-mean from about 12.05 to 3.97. However, visual inspection shows that high transition values
can produce an oversized/cap-like medial corner and narrow-eye combinations can legitimately fail
the existing self-intersection invariant. Therefore **no non-zero default is promoted** and this
micro-brick remains visually open.

Evidence: `docs/components/eyes/morphology/V1.5_MOR_CANTHUS_CURVATURE_PROFILE_CONTRACT.md`,
`artifacts/v15_mor_canthus_curvature_profile/`,
`tools/visual_qa_v15_mor_canthus_curvature_profile.py`,
`tools/verify_v15_mor_canthus_curvature_profile.py`.

Next geometry step: replace the single scalar transition with independently constrained tangent
direction/transition-length controls at each of the four lid-to-canthus endpoints, then calibrate
those controls against digitized samples from the clean reference sheet. The solver must preserve
C1, prevent self-intersection, and reject visually swollen or hooked corners rather than hiding them
with tolerances.

## V1.6 — MOR canthus endpoint tangent profile — 2026-09-18

- [x] four independent endpoint tangent profiles
- [x] local angle / length / influence axes
- [x] V1.5 compatibility at zero influence
- [x] endpoint independence tests
- [x] morphology/opening/rotation/gaze adversarial coverage
- [x] deterministic clean + sampled visual evidence
- [x] fail-closed engineering verifier
- [ ] visual acceptance of non-zero profiles
- [ ] reference-pixel digitization
- [ ] closure/terminal representation that removes the thick canthus cap

**Current status:** `IMPLEMENTED / ENGINEERING PASS / VISUAL ACCEPTANCE OPEN`.

## V1.7 — MOR canthus terminal / closure representation + transform inheritance — 2026-09-18

- [x] replace default finite-gap canthus closure with explicit shared terminal topology
- [x] retain legacy cubic bridge as explicit `mode="bridge"` only
- [x] make continuity report distinguish shared terminal from C1 bridge continuity
- [x] add medial lacrimal-caruncle geometry as a separate curved ocular-surface detail
- [x] mirror medial corner/caruncle ownership correctly across paired eyes
- [x] separate parent/eye rotation from internal gaze semantics
- [x] inherit eye rotation + local brow angle in the eyebrow renderer
- [x] prevent endpoint lash roots from recreating a false canthus cap
- [x] add sparse lower-lash deterministic floor after terminal exclusion
- [x] add V1.7 unit tests and full-suite regression
- [x] deterministic clean + sampled visual evidence
- [x] inspect inner/outer close-ups and paired ±30° rotation artifacts
- [x] fail-closed verifier
- [ ] reference-pixel digitization and numeric calibration
- [ ] generic runtime world-transform injection into the ocular builder

**Current status:** `IMPLEMENTED / ENGINEERING PASS / DEFAULT VISUAL REVIEWED / REFERENCE CALIBRATION OPEN`.

The important correction is architectural: the canthus is now a terminal topology owned by the lid margins rather than a full-width closure stroke, while the medial caruncle is a separate internal feature. The V1.6 endpoint tangent profiles remain available and operate on the actual lid geometry. Parent rotation and gaze are no longer conflated: parent rotation is inherited by the brow, while gaze moves the internal iris/pupil assembly.

Evidence: `docs/components/eyes/morphology/V1.7_MOR_CANTHUS_TERMINAL_TRANSFORM_CONTRACT__part_01.md` (split document; see adjacent parts),
`tools/visual_qa_v17_canthus_terminal_transform.py`,
`tools/verify_v17_canthus_terminal_transform.py`,
`artifacts/v17_canthus_terminal_transform/`.

### V1.7 visual acceptance note

The default shared-terminal close-ups were inspected after an additional lash-terminal correction. The first V1.7 render still showed a residual outer-corner lash mass; the lash terminal exclusion was tightened before final evidence generation. This correction is recorded deliberately rather than hiding the failed visual pass behind numerical continuity tests.

No reference-pixel fit is claimed because the original source reference sheets are not present in the checkpoint.

### Artifact retention policy — 2026-09-18

The working checkpoint retains only the latest V1.7 visual evidence directory. Superseded V1.3–V1.6 generated artifacts were removed after the V1.7 evidence set was verified. Historical source/docs remain; old artifact paths in historical documents describe past evidence and are not current retained files.

## V1.8 — Reference Digitization + Ocular Transform Resolution — 2026-09-18

- [x] increase default brow-to-eye clearance while keeping it explicitly overridable
- [x] keep brow clearance stable through opening, closed/covered state, gaze and parent rotation
- [x] correct paired brow translation/rotation so each brow remains attached to its own eye
- [x] remove gaze-driven brow translation
- [x] point-taper upper/lower lid terminals to remove visual canthus caps
- [x] make explicit finite-gap bridge rendering gap-aware and fail visually closed for tiny gaps
- [x] move caruncle/epicanthic details underneath lid borders and clip to the aperture
- [x] inset epicanthic fold endpoints from the canthal border
- [x] expose the existing runtime root→target world transform through an ocular façade
- [x] implement reference digitization data structures and independent tangent/detail measurements
- [x] keep human/anime/exaggerated family labels separate
- [x] add explicit source-pixel provenance gate
- [x] adversarial transform tests: translation, rotation, uniform/non-uniform scale, nested hierarchy, ±30/±45/+90 and gaze separation
- [x] deterministic visual QA and envelope-only reference evidence
- [x] performance comparison against the extracted V1.7 checkpoint
- [x] remove superseded V1.7 generated artifacts after verification
- [ ] populate actual reference contour/tangent/caruncle/epicanthic coordinates when the original pixel sheets are supplied
- [ ] fit reference-derived numeric style bands only after pixel digitization and human visual acceptance

**Current status:** `IMPLEMENTED / ENGINEERING PASS / VISUAL REVIEWED / PIXEL DIGITIZATION SOURCE GATED`.

The critical architectural rule remains: reference pixels are evidence, not a source of invented coordinates. V1.8 therefore implements the complete digitization/measurement machinery but refuses to call the current envelope-only dataset a pixel reconstruction.

Evidence: `docs/components/eyes/reference/V1.8_REFERENCE_DIGITIZATION_OCULAR_TRANSFORM_CONTRACT__part_01.md` (split document; see adjacent parts), `tools/visual_qa_v18_reference_digitization_ocular_transform.py`, `tools/verify_v18_reference_digitization_ocular_transform.py`, `artifacts/v18_reference_digitization_ocular_transform/`.

### V1.8 artifact retention policy

After V1.8 verification, the superseded `artifacts/v17_canthus_terminal_transform/` directory is removed. Historical source/docs remain; only the latest generated/sampled V1.8 evidence is retained under `artifacts/`.
