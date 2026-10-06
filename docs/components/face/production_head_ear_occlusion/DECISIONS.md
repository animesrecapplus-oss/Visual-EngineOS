# Decisions

`DEC-HEO2-001`: relation selected from measured 15.55%/21.84% real overlap, not from a deferred feature list.
`DEC-HEO2-002`: target remains Ear; HumanFace head is the occluder because renderer paint order places head after ear.
`DEC-HEO2-003`: use explicit `coplanar_occludes=True`; do not invent negative depth or change existing depth layers.
`DEC-HEO2-004`: do not claim attribution until a real downstream consumer exists.
