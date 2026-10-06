# Invariants and assumptions — CMP-FACE-MOUTH

## Invariants

- `INV-MOUTH-001`: width and height are finite and strictly positive before geometry construction.
- `INV-MOUTH-002`: generated radii are positive finite halves of the authored dimensions.
- `INV-MOUTH-003`: every production mouth surface has `depth_layer=1` and a non-empty owner.
- `INV-MOUTH-004`: the production composite has exactly one Mouth dependency and cannot depend on itself.
- `INV-MOUTH-005`: visibility occluder IDs and depths are aligned, unique and never contain the target.
- `INV-MOUTH-006`: cache identity changes when authored mouth geometry changes.
- `INV-MOUTH-007`: zero resolved visibility removes mouth SVG emission through the generic renderer.
- `INV-MOUTH-008`: the leaf rejects bool/string/non-finite malformed dimensions before float coercion.
- `INV-MOUTH-009`: positive dimensions must produce strictly positive representable radii.

## Assumptions

The generic `Parameter`, `GeometryContract`, `VisualContract`, cache and persistence contracts remain authoritative.
No assumption is made that the mouth solves lips, teeth, tongue or expression morphology.
