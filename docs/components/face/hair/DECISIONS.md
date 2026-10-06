# Decisions — CMP-FACE-HAIR

`DEC-FH-001`: V1.57 selects Hair production because the certified V1.56 tree contained a real HumanFace Hair child and production consumer boundary.

`DEC-FH-002`: keep one bounded cap; do not bundle strands, morphology or accessories.

`DEC-FH-003`: V1.58 changes the Hair authored depth to `1` because real Hair/Ear overlap exists and the renderer already paints Hair after Ear.

`DEC-FH-004`: Hair/Ear visibility is owned by `CMP-PROD-HAIR-EAR-OCCLUSION`, not by the Hair leaf.

`DEC-FH-005`: preserve explicit previous generators and do not alter COLOR or database schema without an independent consumer.
