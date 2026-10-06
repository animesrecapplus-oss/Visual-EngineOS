<!-- Refactored from docs/governance/roadmap/ROADMAP__part_01.md; source lines 1202-1329; content preserved. -->
<!-- Part 10/16. Use the family index for navigation. -->
## V1.9 — Reference Pixel Acquisition + Digitized Ocular Calibration — 2026-09-18

- [x] verify V1.8 pair-rotation defect against generated artifacts
- [x] rotate binocular anchors rigidly around their midpoint for 0/±30/±45/90°
- [x] preserve left/right local eye orientation while rotating the pair axis
- [x] correct closed-eye rotation by flattening in local frame before parent transform
- [x] resolve explicit gaze targets in eye-local coordinates before aperture solving
- [x] inherit parent rotation by iris/pupil assembly and reflection center
- [x] add exact reference-source hash/dimension acquisition gate
- [x] add temporary download + fail-closed verification path
- [x] add grid-independent segmentation proposal engine
- [x] add four independent endpoint tangent/curvature/transition measurement machinery
- [x] add caruncle color/opacity fields without treating missing observations as zero
- [x] locate candidate source for asset 53267426 without falsely admitting it as verified original
- [x] explicitly record unresolved second reference source
- [x] deterministic visual QA with real clean + sampled pair/closed-eye artifacts
- [x] keep reference overlay blocked while exact source pixels are unavailable
- [ ] acquire and verify exact original pixels for both reference sheets
- [ ] visually review segmentation candidate boxes
- [ ] digitize upper/lower contours from actual pixels
- [ ] digitize medial/lateral terminals and four endpoint tangents
- [ ] digitize caruncle geometry/color/opacity where visible
- [ ] digitize epicanthic fold only where the pixels support the identification
- [ ] assign reference family labels from observable construction evidence
- [ ] generate true reference-vs-engine overlays and error maps
- [ ] calibrate numeric style bands only after human visual acceptance

**Current status:** `ENGINEERING PASS / TRANSFORM CORRECTION VERIFIED / PIXEL CALIBRATION BLOCKED BY SOURCE VERIFICATION`.

Evidence: `docs/components/eyes/reference/V1.9_REFERENCE_PIXEL_ACQUISITION_OCULAR_CALIBRATION_CONTRACT.md`, `tools/visual_qa_v19_reference_pixel_acquisition_ocular_calibration.py`, `tools/verify_v19_reference_pixel_acquisition_ocular_calibration.py`, `artifacts/v19_reference_pixel_acquisition_ocular_calibration/`.

### V1.10 — True Pixel Digitization + Reference/Engine Overlay + Alignment-Axis Rotation — 2026-09-18

- [x] formalize screen-plane roll vs alignment-axis depth rotation
- [x] add `alignment_axis_rotation_deg` to eye morphology
- [x] project ocular geometry through alignment-axis foreshortening, then roll
- [x] project iris/pupil/reflection ellipses with inherited orientation
- [x] inherit alignment-axis rotation through ocular children and semantic parent transforms
- [x] add bilateral alignment-axis asymmetry policy
- [x] add prompt-facing ocular intent names, including `look_behind_right_eye`
- [x] add source format/orientation inspection and crop-status provenance gate
- [x] byte-preserve uploaded reference sheet with digest-guarded no-overwrite
- [x] implement human-review segmentation queue
- [x] implement explicit approved-region + component-selection gate
- [x] implement dense pixel trace candidate extraction
- [x] implement explicit pixel↔engine overlay mapping and inverse mapping
- [x] implement real overlay renderer for approved samples
- [x] generate synthetic self-consistent overlay to verify overlay wiring
- [x] generate clean orientation renders and reference candidate review artifact
- [x] add adversarial unit tests for axis composition, parent inheritance, persistence, prompt semantics and overlay gates
- [x] full-suite regression and compile check
- [ ] human-review candidate boxes from the uploaded sheet
- [ ] approve concrete eye regions and select upper/lower ink components
- [ ] digitize actual upper/lower contours at dense resolution
- [ ] digitize four independent endpoint tangents and transition lengths
- [ ] digitize canthus terminal/convergence/curvature
- [ ] digitize caruncle only where source pixels support it
- [ ] digitize epicanthus only where source pixels support it
- [ ] assign observable family labels without overgeneralising from style
- [ ] generate true source-pixel reference-vs-engine overlays
- [ ] generate quantitative error maps per structural field
- [ ] calibrate canthus/terminal style bands only after visual acceptance
- [ ] add perspective-aware view-axis/yaw backend for genuine 3D side/back gaze

**Current status:** `ENGINEERING PASS / ALIGNMENT-AXIS ROTATION IMPLEMENTED / PIXEL SOURCE PRESERVED / HUMAN DIGITIZATION PENDING / REAL CALIBRATION NOT YET PROMOTED`.

Evidence: `docs/components/eyes/reference/V1.10_TRUE_PIXEL_DIGITIZATION_REFERENCE_OVERLAY_AND_ALIGNMENT_AXIS_CONTRACT__part_01.md` (split document; see adjacent parts), `tools/visual_qa_v110_alignment_axis_and_reference_review.py`, `artifacts/v110_alignment_axis_and_reference_review/`.

## V1.11 — Human-Validated Pixel Calibration — 2026-09-18

- [x] create an immutable review state machine for all 28 V1.10 segmentation candidates
- [x] enforce `approved + sample_id` and reject illegal review states
- [x] generate a compact numbered 28-candidate review board and sampled crop montage
- [x] replace x-axis-only trace sampling with orientation-independent dense centerline proposals
- [x] explicitly orient approved upper/lower traces from inner/medial toward outer/lateral
- [x] preserve independent inner-upper, inner-lower, outer-upper, outer-lower measurements
- [x] formalize terminal semantics and front-view x-order sanity checks
- [x] add pixel canthus convergence/transition/curvature measurements
- [x] add explicit caruncle measurement contract
- [x] add explicit epicanthus present/absent/unknown gate
- [x] extend overlay metrics with four tangent errors and terminal errors
- [x] require two independently approved samples before MOR range promotion
- [x] define MOR confidence as coverage-only, not anatomical/statistical confidence
- [x] run full regression: 599 passed, 1 skipped
- [x] run compileall and deterministic V1.11 verifier
- [ ] human-review the 28 candidates from the supplied sheet
- [ ] approve concrete eye regions and sample IDs
- [ ] select exact upper/lower ink components for approved samples
- [ ] mark inner/outer terminals and eye side for each approved sample
- [ ] digitize caruncle/epicanthus only where visually supported
- [ ] generate first real source-pixel overlay for approved samples
- [ ] generate quantitative per-field error maps
- [ ] aggregate first MOR observed ranges from >=2 approved samples

**Current status:** `ENGINEERING PASS / REVIEW QUEUE READY / REAL PIXEL CALIBRATION BLOCKED UNTIL EXPLICIT HUMAN APPROVAL`.

Evidence: `docs/components/eyes/reference/V1.11_HUMAN_VALIDATED_PIXEL_CALIBRATION_CONTRACT__part_01.md` (split document; see adjacent parts), `tools/visual_qa_v111_human_validated_pixel_calibration.py`, `tools/verify_v111_human_validated_pixel_calibration.py`, `artifacts/v111_human_validated_pixel_calibration/`.

## V1.13 — Spherical Eyeball + Eyelid/Globe Decoupling — 2026-09-18

- [x] add explicit ocular 3D basis (`alignment`, `vertical`, `view`)
- [x] separate yaw, pitch, roll and alignment-axis semantics
- [x] compose parent/child ocular orientation through bases rather than Euler addition
- [x] keep yaw/pitch out of the generic 2D transform matrix
- [x] add parametric spherical globe center/radius
- [x] project sphere silhouette from 3D geometry
- [x] project iris circle from an oriented globe surface
- [x] project pupil from the same ocular surface frame
- [x] add separate corneal projection marker
- [x] keep eyelid aperture as an independent geometry owner and clipping boundary
- [x] expose independent near/far canthus and ocular-surface visibility diagnostics
- [x] support single-eye and independent multi-eye backward orientations
- [x] add perspective camera safety checks
- [x] bump eye geometry generator cache version from 2 to 3
- [x] add adversarial V1.13 unit tests
- [x] generate clean and sampled visual QA artifacts
- [x] execute full repository regression
- [x] remove caches before checkpoint packaging
- [x] create dedicated V1.13 contract and verifier
- [ ] implement physically coupled eyelid-on-globe surface sliding
- [ ] implement true 3D canthus depth/near-far visibility
- [ ] implement corneal optical/refraction model
- [ ] calibrate 3D orientation against human-approved V1.11 pixels

**Current status:** `V1.13 ENGINEERING PASS / VISUAL QA PASS / FULL REGRESSION PASS WITH 1 EXISTING ENVIRONMENT SKIP`.

Evidence: `docs/components/eyes/reference/V1.13_SPHERICAL_EYEBALL_EYELID_GLOBE_DECOUPLING_CONTRACT__part_01.md` (split document; see adjacent parts), `tools/visual_qa_v113_spherical_eyeball.py`, `tools/verify_v113_spherical_eyeball.py`, `artifacts/v113_spherical_eyeball/`.
