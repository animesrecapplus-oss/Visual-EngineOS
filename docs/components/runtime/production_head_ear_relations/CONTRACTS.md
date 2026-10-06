# Contracts

`CON-PHER-001`: root is the existing `HumanFace` production component containing `left_ear` and `right_ear`.

`CON-PHER-002`: camera geometry is already transformed `GeometryContract`; this component does not regenerate or transform it.

`CON-PHER-003`: Head style is an existing `ResolvedVisualContract`; effective visibility and material transmission are forwarded unchanged.

`CON-PHER-004`: owner geometry/depth is delegated through the canonical injected callable.

`CON-PHER-005`: result order is exactly `(left_ear, right_ear)`.

`CON-PHER-006`: one-pair coplanar visibility remains owned by `production_head_ear_occlusion` and its generic dependencies.
