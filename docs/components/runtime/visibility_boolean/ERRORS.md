# Errors and corrections — CMP-VBOOL-001

- `ERR-VBOOL-001`: first implementation routed `resolve_visibility` through low-level extracted helpers and measured +11.941% median cost. It was not certified.
- `ERR-VBOOL-002`: the initial hostile test assumed `GeometryContract` itself rejected negative ellipse radii; evidence showed materialization owns that validation. Test was corrected to exercise the actual public boolean path.
- `ERR-VBOOL-003`: temporary V1.75 visual board initially used the V1.74 filename prefix; corrected and rerun before final evidence.
- `ERR-VBOOL-004`: `test_legacy_visibility_imports_remain_compatible` exposed a missing historical region-geometry re-export after extraction; the exact legacy imports were restored and the affected suite passed.
- `ERR-VBOOL-005`: no unresolved implementation error remains after the corrections above.

Historical mistakes are retained here rather than rewritten as if they never occurred.
