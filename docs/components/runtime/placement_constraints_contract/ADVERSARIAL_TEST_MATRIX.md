# Adversarial test matrix — CMP-RUNTIME-PLACEMENT-CONSTRAINT-CONTRACT

- `ADV-PCON-001`: NaN tolerance → reject.
- `ADV-PCON-002`: ±∞ tolerance/distance → reject.
- `ADV-PCON-003`: negative tolerance/distance → reject.
- `ADV-PCON-004`: frozen mutation → reject.
- `ADV-PCON-005`: violated result embedded in final solution → reject.
- `ADV-PCON-006`: metadata ordering → deterministic.
- `ADV-PCON-007`: legacy/public identity → same canonical objects.
- `ADV-PCON-008`: import dependency cycle → none introduced.
- `ADV-PCON-009`: production render output → unchanged hashes.
