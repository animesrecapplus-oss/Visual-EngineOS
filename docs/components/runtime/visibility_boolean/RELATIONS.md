# Relations — CMP-VBOOL-001

- `REL-VBOOL-001`: `runtime.visibility` is the historical compatibility facade for boolean API names.
- `REL-VBOOL-002`: `runtime.__init__` exposes the canonical boolean owner.
- `REL-VBOOL-003`: `region_geometry` materializes `GeometryContract` before this component performs planar composition.
- `REL-VBOOL-004`: `visibility.resolve_visibility` remains the owner of depth/optical/event semantics.
- `REL-VBOOL-005`: `visibility_attribution` remains a sibling consumer of `region_geometry`; it is not redirected through this brick.
- `REL-VBOOL-006`: `coverage` retains its compatibility adapter relationship to the visibility kernel.
