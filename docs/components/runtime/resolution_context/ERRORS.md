# Errors

`ERR-RC-001`: non-finite or out-of-range `shadow_alpha` raises `ValueError`.

`ERR-RC-002`: malformed colors, empty names, duplicate mapping keys and duplicate effect IDs raise `ValueError`.

`ERR-RC-003`: wrong `VisualEffect` / `StateActivation` / state-priority types raise `ValueError` at the contract boundary.

No new production error behavior was introduced; V1.67-compatible failures remain enforced by the canonical owner.
