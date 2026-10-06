# Contracts

`CON-PHER-001`: root is a `Component` containing the real `hair`, `left_ear` and `right_ear` children.

`CON-PHER-002`: camera geometry is the already-resolved `GeometryContract`; this component does not regenerate or transform it.

`CON-PHER-003`: Hair style is an existing `ResolvedVisualContract`; effective visibility and material transmission are forwarded unchanged.

`CON-PHER-004`: owner geometry is delegated through the canonical injected callable.

`CON-PHER-005`: result order is exactly `(left_ear, right_ear)`.

`CON-PHER-006`: one-pair validation and generic visibility/attribution remain owned by `production_hair_ear_occlusion` and its generic dependencies.
