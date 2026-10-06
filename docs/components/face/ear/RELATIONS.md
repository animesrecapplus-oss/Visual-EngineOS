# Relations — CMP-FACE-EAR

- `REL-FE-001`: `HumanFace → left_ear/right_ear` parent-child relation.
- `REL-FE-002`: `Ear → Ear composite` consumer relation.
- `REL-FE-003`: `Ear geometry → GeometryContract → generic renderer` downstream relation.
- `REL-FE-004`: `Ear → generic cache/fingerprint` through existing generator infrastructure.
- `REL-FE-005`: malformed parameter → leaf validation failure; no geometry, cache entry or renderer output is produced.
