# Relations — CMP-FACE-HAIR-COMPOSITE

Parent: `HumanFace`.
Siblings: `Eye`, `Nose`, `Mouth`, `Ear`.

Child components: none in V1.57.

`REL-FHC-001`: HumanFace owns the authoring child.
`REL-FHC-002`: Hair geometry is consumed by the Hair-inclusive production composite.
`REL-FHC-003`: SVG rendering is downstream; Hair does not import the renderer.
`REL-FHC-004`: Hair does not participate in the existing head/nose/mouth visibility proof.
`REL-FHC-005`: Hair/ear occlusion is intentionally not represented as implemented.
