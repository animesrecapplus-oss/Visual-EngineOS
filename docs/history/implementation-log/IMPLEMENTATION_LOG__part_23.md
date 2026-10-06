# Implementation log — V1.78

V1.78 corrected the default HumanFace visual calibration after artifact sampling. The previous V1.77 board had repeated one canonical face and did not exercise the existing variation controls.

The new validation sampled ear alignment, eye shape, hair form and detail density, nose/mouth spacing, face proportions and authored colors. One real integration regression was caught when initial hair detail used a second depth layer for the same owner; the production owner-depth invariant rejected it. A second real regression was caught when the revised hair silhouette no longer overlapped ears sufficiently for the existing optical relation; side locks were extended and the affected suite passed.

The final implementation preserves unchanged head and eye owner geometry across normal/boundary/interaction cases while intentionally changing only the calibrated face owners.

## V1.79 — Face structural granularity audit

Implemented a read-only face granularity map and horizontal progression policy from the certified V1.78 checkpoint. Reopened the V1.78 visual board, verified current source owners and real consumers, identified missing micro-component traceability, and added the Nose truth dossier. No runtime geometry or rendering behavior was modified.

Artifacts: `artifacts/current/v1.79/V1.79_FACE_GRANULARITY_AUDIT.json` plus the V1.79 truth dossiers.

## V1.80 — Ear input-boundary hardening

Started from the certified V1.79 checkpoint and repeated the read-only audit. Selected the existing Ear leaf as a different mature micro-component. Implemented strict numeric/finite validation only at the Ear generator boundary for malformed Component state; valid production geometry and all downstream ownership remain unchanged.

Added V1.80 hostile tests for NaN, ±∞, bool and string values; integrated the existing Ear production, head-ear occlusion and hair-ear relation suites. Updated the Ear truth dossier and exact line-range manifest. Hair's proposed hierarchy remains PLANNED only.
