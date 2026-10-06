# Invariants and assumptions

`INV-FOV-001`: target and every occluder ID are distinct and unique.
`INV-FOV-002`: every occluder resolves to exactly one semantic area region.
`INV-FOV-003`: visibility and attribution are delegated; this component never reimplements their geometry.
`INV-FOV-004`: owner extraction remains outside this component and is injected explicitly.
`INV-FOV-005`: extraction must preserve exact SVG, geometry cache key and visibility metrics.
`INV-FOV-006`: no database or COLOR side effect is permitted.

Assumption: the existing production owner extractor continues to enforce explicit depth-layer consistency for this Head/Nose/Mouth path.
