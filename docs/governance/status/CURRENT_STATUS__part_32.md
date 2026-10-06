# Current status — V1.90 architectural audit

## V1.90 — Universal Visual Context Audit

Status: **AUDIT_COMPLETE / NO_RUNTIME_CHANGE**.

Baseline is the exact V1.89 certified package SHA-256 `9976b39d9e8a569bae7fe74176f9f0c023c9370947fd50b6f7652da3168b7a2c`.

The audit verifies, one by one, the existing prompt/compiler, component graph, relations, morphology, constraints, camera, projection, composition, appearance, COLOR, material, optics, lighting, visibility, occlusion, procedural, temporal, persistence, cache, production-render and visual-QA surfaces.

### Confirmed existing surfaces

- mandatory visual execution loop;
- recursive component architecture and truth dossiers;
- RuntimeGraph topology and stale-graph protection;
- 2D Camera + local/world/scene/camera transform chain;
- Frame, Placement, CompositionPolicy and Shot vocabulary;
- production HumanFace render session;
- appearance-domain contracts;
- BASE, MATERIAL and COLOR authoritative resolution seams;
- deterministic geometry cache identity;
- ocular prompt vocabulary;
- canonical bilateral EyePair path.

### Confirmed architectural gaps/defects

1. Generic prompt compiler remains roadmap work; ocular prompt vocabulary is not a general compiler.
2. `Camera()` is a numeric identity fallback, not a certified semantic default viewpoint/framing policy.
3. HumanFace production eye construction drops bilateral side identity: `_eye_component_inputs()` leaves `EyeGeometryInputs.side` at `"single"`.
4. The specialized ocular renderer has an aperture clip, while generic production SVG rendering emits iris/pupil primitives without an equivalent generic mask/clip boundary.
5. A universal child→parent feasibility contract is not established.
6. A universal per-brick production vertical-slice gate is not yet formalized as a mandatory component-development gate.
7. COLOR is established and intentionally bounded; the missing piece is clearer separation/integration with the broader Appearance architecture, not a second COLOR engine.
8. Full lighting/material/optical intelligence, generic style compiler and animation remain planned rather than silently promoted.

No runtime code is changed by V1.90. The next implementation must reopen V1.89 and apply the full VERIFY→CERTIFY protocol before touching a proven owner.
