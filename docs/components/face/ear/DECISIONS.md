# Decisions — CMP-FACE-EAR

- `DEC-FE-001`: use one closed Bézier silhouette; no inner-ear morphology is invented.
- `DEC-FE-002`: reuse the generic `GeometryContract`; no ear renderer is added.
- `DEC-FE-003`: ear paint precedence remains the existing renderer role (`ear`) rather than a negative depth value.
- `DEC-FE-004`: no COLOR or database semantic change is justified by this component.
- `DEC-FE-005`: V1.80 hardens the existing leaf boundary instead of creating an Ear subcomponent; malformed component state is rejected rather than silently coerced.
