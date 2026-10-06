<!-- Refactored from docs/governance/roadmap/ROADMAP__part_01.md; source lines 1470-1601; content preserved. -->
<!-- Part 12/16. Use the family index for navigation. -->
## V1.20 — Human Review → Real Pixel Calibration — 2026-09-20

- [x] verify the exact preserved V1.11 source bytes before calibration work
- [x] reproduce and lock the 28 segmentation candidates
- [x] create explicit human-review records for every candidate
- [x] require explicit eye identity instead of inferring anatomy from segmentation
- [x] require explicit image-left/image-right/single classification
- [x] require explicit upper and lower trace selections
- [x] require explicit medial and lateral terminal coordinates
- [x] distinguish caruncle `present`, `absent`, and `unknown`
- [x] distinguish epicanthus `present`, `absent`, and `unknown`
- [x] preserve observable family classification without universalizing style
- [x] require unique sample IDs only after approval
- [x] preserve contextual face panels as candidates instead of silently splitting them
- [x] connect approved decisions to the existing source-pixel digitizer
- [x] build a fixed terminal-axis/normal-span reference↔engine comparison frame
- [x] compute real upper/lower mean/RMS/max errors
- [x] compute all four endpoint tangent errors and both terminal errors
- [x] aggregate only strengths actually evaluated by every approved sample
- [x] keep fitted results `candidate_only`
- [x] correct the outer-endpoint tangent comparator bug discovered during self-review
- [x] generate visible 28-candidate review board and crop montage
- [x] add deterministic V1.20 verifier
- [x] preserve fail-closed status with zero human approvals
- [ ] complete human review of the 28 candidates
- [ ] digitize the first explicitly approved sample from source pixels
- [ ] digitize at least two independent approved samples
- [ ] evaluate follow-strength sweep on every approved sample
- [ ] generate source/reference ↔ engine overlays for every tested strength
- [ ] inspect visual morphology at the numerical candidate
- [ ] reject numerically improved but visually incorrect candidates
- [ ] promote a calibrated follow-strength value/range only after explicit visual acceptance
- [ ] calibrate the remaining ocular depth/optical parameters using the same approved pixel set

**Current status:** `V1.20 ENGINEERING PASS / HUMAN REVIEW PACKET READY / REAL PIXEL CALIBRATION BLOCKED BY ZERO EXPLICIT APPROVALS`.

Evidence: `docs/components/eyes/reference/V1.20_HUMAN_REVIEW_REAL_PIXEL_CALIBRATION_CONTRACT__part_01.md` (split document; see adjacent parts), `tools/visual_qa_v120_human_review_pixel_calibration.py`, `tools/verify_v120_human_review_pixel_calibration.py`, `artifacts/history/v1.20/human_review_pixel_calibration/`.

## V1.21 — Source-Pixel Trace Capture / Difficult-Contour Workbench — 2026-09-20

- [x] inspect the actual V1.20 source-pixel component inventory across all 28 candidates
- [x] identify the component-only blind spot without assigning anatomy automatically
- [x] add an explicit reviewer-selected smaller trace region
- [x] add explicit component/manual trace modes
- [x] preserve raw manual source-pixel polylines without curve fitting
- [x] add explicit reserved manual upper/lower trace identifiers
- [x] reject mixed manual/component ambiguity
- [x] keep V1.20 human semantic approval as a hard prerequisite
- [x] create offline browser trace-capture workbench
- [x] generate all-28 component inventory artifact
- [x] generate focused candidate-014 one-component evidence artifact
- [x] browser-smoke-test the workbench on candidate 014 with 28 candidates loaded
- [x] add deterministic V1.21 verifier
- [x] test real-source smaller-region component digitization
- [ ] execute explicit human review of the 28 candidates
- [ ] approve and digitize first real source sample
- [ ] approve and digitize second independent source sample
- [ ] generate source↔engine overlays for all follow-strength candidates
- [ ] inspect numerical candidate visually and reject visually incorrect morphology
- [ ] promote only after explicit visual acceptance

**Current status:** `V1.21 ENGINEERING PASS / TRACE CAPTURE READY / 28 HUMAN REVIEWS STILL PENDING / CALIBRATION CLOSED`.

Evidence: `docs/components/eyes/reference/V1.21_TRACE_CAPTURE_CONTRACT__part_01.md` (split document; see adjacent parts), `tools/visual_qa_v121_trace_capture.py`, `tools/verify_v121_trace_capture.py`, `artifacts/history/v1.21/trace_capture/`.

# V1.22 — Dual-Sample Provenance Gate — 2026-09-20

- [x] add immutable source fingerprint to the calibration handoff;
- [x] require an explicitly approved V1.20 semantic record;
- [x] require a completed V1.21 source-pixel digitization;
- [x] require distinct candidate IDs and sample IDs for the two-sample gate;
- [x] reject missing capture, missing digitization, incomplete geometry and source mismatch;
- [x] add real source-pixel diagnostic previews without assigning anatomy;
- [x] verify candidate 001 and difficult candidate 014 visually;
- [x] keep calibration promotion closed at zero human approvals;
- [ ] obtain explicit human review decisions for the 28 candidates;
- [ ] digitize first approved sample with provenance;
- [ ] digitize second independent approved sample with provenance;
- [ ] execute the five-strength source↔engine comparison;
- [ ] render and inspect actual overlays before any candidate selection/promotion.

**V1.22 status:** `ENGINEERING PASS / TWO-SAMPLE GATE READY / 28 REVIEWS STILL PENDING / CALIBRATION CLOSED`.


# V1.29 — Typed Appearance Input Promotion — 2026-09-23

- [x] define a canonical renderer-neutral `TypedAppearanceInput` envelope
- [x] make `AppearanceRoleContribution` the authoritative selected BASE/COLOR role hand-off
- [x] keep legacy `base_color` explicitly derived at the compatibility boundary
- [x] make the BASE domain resolver consume typed role data on the canonical path
- [x] reject a typed role combined with a second legacy BASE authority
- [x] propagate role bridge fingerprint, authority ID, source ID and lineage into domain provenance
- [x] inject the role bridge fingerprint as an explicit domain dependency identity
- [x] keep geometry/transform/unrelated sibling data out of typed appearance fingerprints
- [x] add typed-input tampering and persistence round-trip coverage
- [x] validate object, hand and plant generic non-ocular components
- [x] generate and manually inspect source → typed → BASE-domain visual evidence
- [x] bump resolution identity from 14 to 15 and BASE resolver identity from 1 to 2
- [x] remove the superseded V1.28 working artifact directory from the current checkpoint
- [ ] deprecate the legacy `AppearanceResolutionInput.base_color` field only after downstream callers have migrated
- [ ] promote the typed envelope through every remaining domain resolver that genuinely consumes color
- [ ] add equivalent typed-role provenance to Palette/Color domain consumers when their semantics are implemented
- [ ] keep renderer-independent material/light/color algorithms separate from this input-promotion layer

**V1.29 status:** `ENGINEERING PASS / TYPED INPUT CANONICAL PATH VERIFIED / VISUAL EVIDENCE INSPECTED / LEGACY FIELD RETAINED FOR COMPATIBILITY`.

Evidence: `docs/domains/color/V1.29_TYPED_APPEARANCE_INPUT_CONTRACT.md`, `docs/domains/color/V1.29_IMPLEMENTATION_REPORT_2026-09-23__part_01.md` (split document; see adjacent parts), `tools/verify_v129_typed_appearance_input.py`, `artifacts/v129_typed_appearance_input/`.


# V1.30 — Typed BASE Consumer Migration — 2026-09-23

- [x] audit every source consumer of `AppearanceResolutionInput.base_color` / `build_appearance_input()`
- [x] classify the remaining production uses as compatibility definition, typed→legacy bridge, or explicit legacy escape hatch
- [x] add direct `TypedAppearanceInput.to_base_domain_input()` hand-off
- [x] add `build_base_resolution_input_from_typed()` and `resolve_base_domain_from_typed()`
- [x] ensure the typed BASE path never manufactures a legacy `AppearanceContribution`
- [x] preserve authored/generated representation and role provenance through the migrated path
- [x] preserve exact `appearance_role_bridge` dependency identity
- [x] add sibling/geometry independence tests and contradictory dependency rejection
- [x] add a static source audit preventing hidden legacy builder consumers
- [x] validate object, hand, plant and Palette-selected hand paths
- [x] generate and manually inspect before/after semantic visual evidence
- [x] remove superseded V1.29 working-artifact directories from the current checkpoint
- [x] bump engine/package version 1.3.5 → 1.3.6 and resolution identity 15 → 16
- [ ] deprecate `AppearanceResolutionInput.base_color` only after external/legacy callers are demonstrably migrated
- [ ] migrate a genuine COLOR-domain consumer only after the COLOR contract defines its non-mixing semantics

**V1.30 status:** `ENGINEERING PASS / LEGACY CONSUMER AUDIT PASS / TYPED BASE PATH MIGRATED / VISUAL EVIDENCE INSPECTED / LEGACY API RETAINED FOR COMPATIBILITY`.

Evidence: `docs/domains/color/V1.30_TYPED_BASE_CONSUMER_MIGRATION_CONTRACT.md`, `docs/domains/color/V1.30_IMPLEMENTATION_REPORT_2026-09-23__part_01.md` (split document; see adjacent parts), `tools/verify_v130_legacy_consumer_migration.py`, `artifacts/v130_legacy_consumer_migration/`.
