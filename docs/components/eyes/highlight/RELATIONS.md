# Relations — CMP-EYE-HIGHLIGHT

- `REL-HIGHLIGHT-001`: Highlight belongs to the `CMP-EYE` aggregate (VERIFIED).
- `REL-HIGHLIGHT-002`: Highlight is a cross-relation ocular reflection system, not a fixed Pupil child (VERIFIED by V1.83 hierarchy matrix).
- `REL-HIGHLIGHT-003`: Renderer positions marks relative to `g.iris_center` and iris radii (VERIFIED at `eye_svg_effects.py:214-220`).
- `REL-HIGHLIGHT-004`: `EyeVisibilitySpec` controls `reflection_marks` visibility (VERIFIED at `visibility.py:24,43-52`).
- `REL-HIGHLIGHT-005`: Appearance/style layers construct or carry marks (VERIFIED).
- `REL-HIGHLIGHT-006`: Pair appearance signatures include marks (VERIFIED at `pair.py:200-205`).
- `REL-HIGHLIGHT-007`: Geometry cache intentionally excludes marks (VERIFIED at `generator.py:192-226`).

No new relation is introduced by V1.88.
