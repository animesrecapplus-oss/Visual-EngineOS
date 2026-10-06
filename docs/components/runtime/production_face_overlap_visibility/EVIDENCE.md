# Evidence

`EVD-FOV-001`: pre-change focused matrix: 44/44 PASS.
`EVD-FOV-002`: post-extraction focused matrix: 44/44 PASS.
`EVD-FOV-003`: certified V1.59 and V1.60 production SVG SHA-256 are identical: `f1b0e82fdb9ad27ad45005454bca7fdf8b31e2cd94124ddc1a2e214252de3db1`.
`EVD-FOV-004`: camera-geometry digest is identical: `0575e83f6460732c3cb80cef300063e55721ad28c63e24dcd7da8a169c8e722e`.
`EVD-FOV-005`: visibility coverage `0.027850204680330913`, visible `0.9721497953196694`, attribution values are identical before/after extraction.
`EVD-FOV-006`: five V1.60 warm benchmark medians are `17,242,449`, `17,567,180`, `17,435,129`, `18,962,889`, `18,357,214 ns`; median `17,567,180 ns`. The V1.59 five-run median was `33,835,366.5 ns`. The measured `-48.08%` change is environment-sensitive and is not claimed as a non-regression.
