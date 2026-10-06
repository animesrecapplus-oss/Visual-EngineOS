# Decisions — V1.90

- `DEC-V190-001`: treat V1.90 as an architecture/traceability audit with no runtime code change.
- `DEC-V190-002`: use the exact V1.89 certified package as the only baseline for this audit.
- `DEC-V190-003`: preserve the existing visual execution loop and add a mandatory per-brick production vertical-slice requirement to the architecture contract; do not replace existing unit/integration/hostile evidence.
- `DEC-V190-004`: distinguish `Camera()` numeric identity fallback from a semantic default viewpoint; no undocumented claim that unspecified prompts are necessarily front-view.
- `DEC-V190-005`: keep camera pose, projection, framing, entity/head orientation and ocular gaze as separate semantic channels.
- `DEC-V190-006`: do not create a generic prompt compiler yet; the existing ocular prompt vocabulary is not promoted into a system-wide parser.
- `DEC-V190-007`: do not create a universal `VisualComponent` mega-class; formalize the universal context as a dossier/contract matrix.
- `DEC-V190-008`: preserve COLOR as its own bounded domain and do not invent a second COLOR algorithm merely to complete Appearance.
- `DEC-V190-009`: classify the HumanFace left-eye side loss as a production integration defect owned at the HumanFace→Eye input boundary, not by Gaze.
- `DEC-V190-010`: classify generic iris/pupil aperture clipping as a render-plan/mask boundary gap; owner remains unpromoted until fresh impact analysis.
- `DEC-V190-011`: treat the canonical EyePair path and the HumanFace production path as distinct consumers requiring separate vertical validation.
- `DEC-V190-012`: future visual-component bricks must account for semantic, structural, morphology, relations, constraints, visibility, occlusion, appearance, COLOR, material, optics, lighting, camera, composition, procedural, temporal, persistence, cache and production evidence axes; `NOT_APPLICABLE` must be explicit.
