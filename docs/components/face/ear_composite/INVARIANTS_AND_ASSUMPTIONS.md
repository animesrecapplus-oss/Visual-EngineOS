# Invariants and assumptions — CMP-FACE-EAR-COMPOSITE

- `INV-FEC-001`: no duplicate/missing ear is silently tolerated.
- `INV-FEC-002`: dependency IDs are deterministic and sorted by the registry contract.
- `INV-FEC-003`: the previous `face.human_with_eyes_nose_mouth` generator remains callable as an explicit compatibility surface.
- `INV-FEC-004`: ear visibility is resolved by the generic appearance resolver, not by composite code.
