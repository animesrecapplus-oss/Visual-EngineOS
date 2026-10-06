# Adversarial test matrix

`ADV-RC-001`: NaN / +∞ / -∞ / negative / >1 `shadow_alpha` → rejected.

`ADV-RC-002`: malformed hexadecimal color → rejected.

`ADV-RC-003`: empty occlusion/state names → rejected.

`ADV-RC-004`: wrong state-priority/effect/state-activation runtime types → rejected.

`ADV-RC-005`: duplicate state-map keys and duplicate effect IDs → rejected.

`ADV-RC-006`: shuffled states/effects/consequence states → canonical deterministic order.

`ADV-RC-007`: global, targeted and unrelated effects → target filtering preserved.

`ADV-RC-008`: public/facade/canonical class identity → one owner only.

`ADV-RC-009`: selected owner importing legacy facade → forbidden by dependency inspection.

`ADV-RC-010`: import-cycle audit and exact-function duplicate audit → 3 pre-existing SCCs, 0 new SCC, 0 exact duplicate groups.

`ADV-RC-011`: production five-case behavior identity → required before certification.
