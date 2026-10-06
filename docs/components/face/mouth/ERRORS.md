# Error register — CMP-FACE-MOUTH

- `ERR-MOUTH-001` — historical registry SCC during first production integration; corrected by the separate production registry owner.
- `ERR-MOUTH-002` — historical compatibility tests selected the new default; corrected with explicit historical generators.
- `ERR-MOUTH-003` — historical visual QA board label overlap; corrected before final evidence.
- `ERR-MOUTH-004` — V1.81 audit reproduced a leaf-boundary gap: bypassed `Parameter` values could be coerced with `float()`.
  The gap affected bools, numeric strings and positive subnormal values that could become zero radii.

V1.81 closes `ERR-MOUTH-004` without changing valid geometry. The stylized ellipse remains intentionally limited and is
not promoted to full lip/teeth/tongue morphology.
