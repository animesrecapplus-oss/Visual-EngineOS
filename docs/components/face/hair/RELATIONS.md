# Relations — CMP-FACE-HAIR

Parent: `HumanFace`.
Siblings: `Eye`, `Nose`, `Mouth`, `Ear`.

Child components: none in V1.57.

`REL-FH-001`: HumanFace owns the authoring child.
`REL-FH-002`: Hair geometry is consumed by the Hair-inclusive production composite.
`REL-FH-003`: SVG rendering is downstream; Hair does not import the renderer.
`REL-FH-004`: Hair does not participate in the existing head/nose/mouth visibility proof.
`REL-FH-005`: Hair/ear occlusion is intentionally not represented as implemented.
