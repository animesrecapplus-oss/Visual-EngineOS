# Decisions — CMP-FACE-MOUTH

`DEC-MOUTH-001` — Preserve the real Mouth production owner and existing ellipse contract.

`DEC-MOUTH-002` — Keep the production registry separate; no second geometry authority is introduced.

`DEC-MOUTH-003` — Use the existing generic ellipse primitive; no renderer-specific mouth branch is added.

`DEC-MOUTH-004` — Use the existing multi-occluder visibility kernel; no second visibility algorithm is introduced.

`DEC-MOUTH-005` — Do not perform COLOR/database work without a real downstream consumer or schema requirement.

## `DEC-MOUTH-006` — V1.81 input-boundary hardening

The generic `Parameter` constructor is authoritative for normal construction, but the Mouth leaf must also protect
its own geometry contract when a malformed `Component` bypasses that constructor. Reject bool/string/non-finite values
and positive dimensions that collapse to zero radii. Keep generator version `1` because valid geometry semantics are unchanged.

## `DEC-MOUTH-007` — No morphology promotion

V1.81 does not create lip, commissure, teeth, tongue, oral-region or expression children. Those remain future micro-components
only when an executable owner, real consumer and independent contract exist.
