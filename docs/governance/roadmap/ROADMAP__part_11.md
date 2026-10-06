<!-- Refactored from docs/governance/roadmap/ROADMAP__part_01.md; source lines 1330-1469; content preserved. -->
<!-- Part 11/16. Use the family index for navigation. -->
## V1.14 — Eyelid / Eyeball Surface Coupling — 2026-09-19

- [x] audit V1.13 artifacts before cleanup
- [x] confirm and document the V1.13 pupil/iris detachment from stored coordinates and rendered evidence
- [x] make iris the parent surface attachment for spherical children
- [x] keep pupil children attached when iris/gaze position changes
- [x] support multiple pupil children through the same parent attachment contract
- [x] replace floating tangent-disc iris/pupil patches with spherical/geodesic surface patches
- [x] store projected surface centers instead of using projected bounding-box centers as semantic anchors
- [x] lift upper/lower eyelid traces onto the globe or explicit orbital shell
- [x] compute near/far canthus from 3D camera depth
- [x] lift caruncle and epicanthic fold as separate surface traces when present
- [x] measure projected iris/pupil aperture clipping without replacing SVG clipping
- [x] preserve closed-eye renderer gating
- [x] cover extreme yaw/pitch plus roll/alignment combinations with adversarial tests
- [x] generate clean and visible sampled QA, including an offset-pupil child case
- [x] remove superseded V1.10/V1.11/V1.13 generated artifact directories after audit
- [x] bump eye geometry generator version from 3 to 4 for surface-attachment cache invalidation
- [x] full repository regression: 627 collected / 626 passed / 1 existing PostgreSQL environment skip
- [x] compileall and line-budget checks
- [ ] physical z-buffer/ray-based eyelid occlusion
- [ ] full 3D facial orbital surface
- [ ] physical corneal refraction/transmission
- [ ] human-approved V1.11 reference calibration

**Current status:** `V1.14 ENGINEERING PASS / FULL REGRESSION PASS WITH 1 EXISTING ENVIRONMENT SKIP / VISUAL QA INSPECTED / REFERENCE CALIBRATION STILL HUMAN-REVIEW GATED`.

Evidence: `docs/components/eyes/reference/V1.13_ARTIFACT_AUDIT_BEFORE_V1.14.md`, `docs/components/eyes/reference/V1.14_EYELID_EYEBALL_SURFACE_COUPLING_CONTRACT__part_01.md` (split document; see adjacent parts), `tools/visual_qa_v114_eyelid_globe_coupling.py`, `artifacts/v114_eyelid_globe_coupling/`.

## V1.15 — True Ocular Depth Occlusion / Orbital Surface — 2026-09-19

- [x] audit useful V1.14 artifacts before replacement
- [x] add explicit procedural orbital ellipsoid surface
- [x] store upper/lower eyelid depth layers
- [x] store iris and every pupil child depth layer from actual 3D samples
- [x] define explicit ocular z-order
- [x] resolve local lid-vs-child depth occlusion near lid margins
- [x] keep the 2D eyelid aperture as the global morphology boundary
- [x] render spherical eyelid margins after ocular children for foreground boundary ownership
- [x] preserve iris → pupil parent-child attachment during depth resolution
- [x] support independent backward/forward eyes and multiple pupil children
- [x] test yaw ±90/±120/±150/180 and pitch ±90 with roll/alignment combinations
- [x] generate clean raster QA and sampled depth-layer diagnostics
- [x] run targeted V1.10–V1.15 regression
- [x] run complete repository suite in deterministic file batches because the monolithic suite exceeds the execution time budget
- [ ] replace procedural orbital ellipsoid with calibrated 3D facial/orbital surface
- [ ] implement continuous ray-based/z-buffer occlusion
- [ ] implement physical corneal transmission/refraction
- [ ] calibrate depth surfaces against human-approved V1.11 pixels

**Current status:** `V1.15 ENGINEERING PASS / DEPTH QA PASS / FULL 636-TEST COLLECTION COVERED BY BATCHED EXECUTION / 635 PASSED / 1 EXISTING ENVIRONMENT SKIP / REFERENCE CALIBRATION STILL HUMAN-REVIEW GATED`.

Evidence: `docs/components/eyes/reference/V1.14_ARTIFACT_AUDIT_BEFORE_V1.15.md`, `docs/components/eyes/reference/V1.15_TRUE_OCULAR_DEPTH_OCCLUSION_ORBITAL_SURFACE_CONTRACT.md`, `tools/visual_qa_v115_true_ocular_depth.py`, `tools/verify_v115_true_ocular_depth.py`, `artifacts/v115_true_ocular_depth/`.

## V1.17 — Alignment-Axis Globe / Face-Aperture Decoupling

**Status:** implemented and targeted/full regression verified; visual QA generated.

This release corrects the ownership error exposed by the alignment artifacts:
`alignment_axis_rotation_deg` is no longer allowed to transform the face-owned
2D eyelid aperture. Instead it rotates the ocular 3D basis inherited by the globe
and its children.

### Implemented

- explicit positive/negative alignment convention;
- face-owned aperture/canthus transform separated from ocular globe transform;
- globe/cornea/iris/pupil share the ocular alignment basis;
- pupil remains an iris child;
- parent alignment inheritance remains compositional;
- stable prompt-facing alignment names;
- projected spherical coordinates converted exactly once from camera +Y-up to the
  historical SVG +Y-down contract;
- hidden projected iris samples are not drawn in sampled QA artifacts;
- superseded V1.15 artifacts audited, documented and removed from active artifacts.

### Acceptance

- 645 tests collected; full run completed successfully with the existing
  environment-dependent PostgreSQL skip;
- compileall `src + tools`: pass;
- focused V1.17/V1.10/V1.13/V1.14/V1.15 regression: pass;
- deterministic V1.17 visual QA: pass;
- active `artifacts/` contains only the current V1.17 artifact directory.

### Next micro-step

**V1.18 — Signed Alignment + Perspective / Surface-Feature Validation**:
validate positive/negative alignment under perspective, asymmetric iris texture
coordinates, corneal highlights, depth-sensitive lid occlusion, and bilateral
opposite-sign alignment without confusing alignment with yaw/pitch or roll.

## V1.18 — Signed Alignment / Eyelid Surface Coupling Correction — 2026-09-20

- [x] reproduce the reported V1.17 visual defect before changing geometry
- [x] identify and correct the spherical adapter's double Y inversion
- [x] preserve semantic canthus anchors while allowing interior lid samples to slide over the globe
- [x] keep globe → cornea → iris → pupil on one ocular parent basis
- [x] keep positive and negative alignment as independent prompt-facing semantics
- [x] derive a conservative globe radius from aperture height / iris scale instead of full eye width
- [x] keep transformed lid depth and projected lid coordinates from one 3D interpolation
- [x] reject non-finite/self-intersecting transformed apertures
- [x] test neutral, ±15, ±30, ±45, ±60, ±75 alignment
- [x] test alignment + roll and alignment + yaw/pitch
- [x] test bilateral same-sign and opposite-sign alignment
- [x] generate clean and sampled artifacts from actual stored geometry
- [x] add deterministic V1.18 verifier
- [ ] calibrate `follow_strength` from human-approved V1.11 pixels
- [ ] calibrate iris/cornea optical attachment against approved reference pixels
- [ ] replace the current qualitative alignment morphology parameter with measured source ranges only after pixel validation

**Current status:** `V1.18 ENGINEERING PASS / SIGNED ALIGNMENT PASS / CHILD-HIERARCHY PASS / VISUAL QA PASS / HUMAN PIXEL CALIBRATION STILL GATED`

Evidence: `docs/components/eyes/reference/V1.18_SIGNED_ALIGNMENT_EYELID_SURFACE_COUPLING_CONTRACT.md`, `tools/visual_qa_v118_signed_alignment_surface_coupling.py`, `tools/verify_v118_signed_alignment_surface_coupling.py`, `artifacts/v118_signed_alignment_surface_coupling/`.

## V1.19 — Explicit Eyelid-Surface Follow Parameter + Human-Gated Calibration — 2026-09-20

- [x] promote V1.18's hidden `follow_strength=0.10` to explicit `EyeParameters.eyelid_surface_follow_strength`
- [x] enforce finite `[0,1]` authoring domain
- [x] propagate the parameter into the actual globe-follow lid kernel
- [x] increment eye generator version so geometry-cache identity changes with the new parameter
- [x] add two-independent-approved-sample calibration gate
- [x] reject pending/rejected/unlabelled review candidates from calibration
- [x] fit only over candidate values actually evaluated by every approved sample
- [x] keep numerical fit as `candidate_only` until explicit human visual acceptance
- [x] generate engine-only follow-strength sweep at 0.00/0.05/0.10/0.15/0.20 and ±45°/0° alignment
- [x] clip diagnostic ocular children to the generated aperture before visual inspection
- [x] add deterministic verifier and fail-closed evidence
- [ ] obtain explicit human approval for V1.11 candidates
- [ ] digitize approved upper/lower source contours and terminals
- [ ] generate real source-pixel overlays for approved samples
- [ ] evaluate follow-strength candidates against at least two independent approved samples
- [ ] inspect clean renders at the candidate value and reject any visually incorrect morphology
- [ ] only then promote a measured follow-strength range/value
- [ ] calibrate iris/cornea optical attachment against the same approved pixel set

**Current status:** `V1.19 CALIBRATION INFRASTRUCTURE PASS / ENGINE SWEEP PASS / NO REFERENCE VALUE PROMOTED / HUMAN APPROVAL REQUIRED`

Evidence: `docs/components/eyes/reference/V1.19_EYELID_SURFACE_FOLLOW_CALIBRATION_CONTRACT.md`, `tools/visual_qa_v119_eyelid_surface_calibration.py`, `tools/verify_v119_eyelid_surface_calibration.py`, `artifacts/history/v1.19/eyelid_surface_calibration/`.
