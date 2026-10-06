# V1.87 — component truth — CMP-EYE-EYEBROW

Identity: `CMP-EYE-EYEBROW` — immutable eyebrow appearance value component.

Responsibility: reject malformed local `BrowSpec` input before appearance, expression and rendering consumers receive it.

Non-responsibility: eyebrow geometry construction, placement/gap resolution, rotation inheritance, visibility hierarchy,
cache policy, COLOR transformation, persistence, renderer orchestration and deeper eyebrow anatomy.

Canonical owner: `src/visual_engine/components/face/eyes/eyebrow/spec.py`.

Inputs: enabled, shape, length, thickness, density, angle_deg, x, y, color, ornament, fade_at_inner,
fade_at_outer, min_eye_gap, max_eye_gap.

Output: immutable `BrowSpec` value or deterministic validation error.

Authority: this owner controls local value validity only. Renderer remains authoritative for visual placement and path
construction. Existing source ranges and style vocabulary are retained.

Lifecycle: constructor validation → immutable use by consumers → object replacement via dataclass `replace` where
higher-level expression/profile code derives variants → destruction by normal object lifetime.
