# V1.87 — errors — CMP-EYE-EYEBROW

- `ERR-EYEBROW-001` — pre-change non-finite `length`, `thickness`, `angle_deg`, `x`, `y` accepted. Closed by V1.87.
- `ERR-EYEBROW-002` — pre-change non-bool `enabled` accepted. Closed by V1.87.
- `ERR-EYEBROW-003` — pre-change numeric strings accepted by untyped fields. Closed by V1.87.
- `ERR-EYEBROW-004` — pre-change huge integer could leak `OverflowError` from `math.isfinite`. Closed by V1.87.

No new implementation error was observed after the impact audit was completed. If a future consumer requires a
resource ceiling or anatomical placement contract, it must be reopened as a new scoped brick rather than silently
added here.
