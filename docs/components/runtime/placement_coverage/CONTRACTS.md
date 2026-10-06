# Contracts — CMP-PCOV-001

- `CON-PCOV-001`: `target_fraction` is finite and in `[0,1]`.
- `CON-PCOV-002`: `tolerance` is finite and in `(0,1)`.
- `CON-PCOV-003`: `max_iterations >= 8`.
- `CON-PCOV-004`: coverage resolution is uniform-scale only; placement rejects coverage with non-uniform scale.
- `CON-PCOV-005`: dimension and coverage constraints remain mutually exclusive.
- `CON-PCOV-006`: source and target anchors must lie in their positive-area regions.
- `CON-PCOV-007`: unreachable requested coverage fails explicitly.
- `CON-PCOV-008`: direct solver calls reject wrong intent type and non-finite anchors/rotation/offsets.
- `CON-PCOV-009`: historical public `CoverageIntent` identity remains unchanged.
