# Contracts — CMP-FACE-EAR

- `CON-FE-001`: generator name `face.ear`, version `1`, kind `Ear`.
- `CON-FE-002`: custom generator inputs are rejected; geometry is derived from component parameters/anchor.
- `CON-FE-003`: width and height must be strictly positive and finite.
- `CON-FE-004`: output is a `GeometryContract` in the component-local frame.
- `CON-FE-005`: exactly one closed `EAR` surface is emitted with `path_index=0` and `depth_layer=0`.
- `CON-FE-006`: no renderer-specific branch or COLOR transformation is emitted by the generator.
- `CON-FE-007`: malformed leaf parameter values that bypass `Parameter` must be numeric, non-boolean and finite; strings are not silently coerced.
- `CON-FE-008`: positive dimensions that underflow to a zero radius are rejected before path construction.
