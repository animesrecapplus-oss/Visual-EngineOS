# V1.87 — relations — CMP-EYE-EYEBROW

- `REL-EYEBROW-001` parent: `ORBIT / PERIOCULAR` — VERIFIED by V1.83 hierarchy matrix.
- `REL-EYEBROW-002` aggregate/public parent: `CMP-EYE` — VERIFIED.
- `REL-EYEBROW-003` siblings: eyelid system, lash system, eyeball branch — VERIFIED architectural relation;
  no linear parent chain is introduced.
- `REL-EYEBROW-004` consumer relation: `EyeAppearance.eyebrow → BrowSpec` — VERIFIED.
- `REL-EYEBROW-005` expression relation: expression solver derives a new `BrowSpec` with `dataclasses.replace` — VERIFIED.
- `REL-EYEBROW-006` renderer relation: `_eyebrow_svg` consumes `BrowSpec` in the production SVG path — VERIFIED.
- `REL-EYEBROW-007` cache relation: eyebrow styling is excluded from `_eye_cache_inputs` — VERIFIED.
- `REL-EYEBROW-008` persistence relation: no verified database representation/migration — VERIFIED absence from current
  migration inventory; no persistence contract is promoted.

No semantic child, gaze-owner, occlusion-owner or morphology-owner is invented by this brick.
