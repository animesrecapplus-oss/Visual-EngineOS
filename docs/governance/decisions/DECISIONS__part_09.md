# Decision register — V1.73

`D-155` — Re-audit the previous compatibility-cycle candidate first; no speculative `resolve_component_contract` extraction is allowed.

`D-156` — Select transform resolution inside `runtime.geometry_transform` because it is a distinct responsibility with a dedicated immutable
value, a real compatibility/public consumer surface and a separate dependency boundary from GeometryContract transformation.

`D-157` — Extract only `GeometryTransformResolution` and transform-resolution helpers. Keep `resolve_geometry_contract` in the existing module.

`D-158` — Preserve all historical public imports through `runtime.geometry_transform`; no unrelated consumer rewiring is required.

`D-159` — Freeze COLOR, database/persistence, cache policy, fingerprint algorithms, visibility semantics and renderer semantics for V1.73.
