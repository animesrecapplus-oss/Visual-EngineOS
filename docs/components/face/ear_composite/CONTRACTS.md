# Contracts — CMP-FACE-EAR-COMPOSITE

- `CON-FEC-001`: generator `face.human_with_eyes_nose_mouth_ears@1` supports `HumanFace`.
- `CON-FEC-002`: exactly two direct `Ear` children are required.
- `CON-FEC-003`: both ear IDs must be present in prepared child geometry.
- `CON-FEC-004`: cache identity includes base face geometry plus both ear geometry digests.
- `CON-FEC-005`: composition remains renderer-neutral and delegates rendering to generic SVG infrastructure.
