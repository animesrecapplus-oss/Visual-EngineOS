# Roadmap — V1.76 and next frontier

## V1.76 — Placement constraint contract ownership extraction

Fresh V1.75 audit selected immutable placement-constraint contracts as a distinct responsibility inside `runtime.placement_constraints`.

Owner: `runtime/placement_constraints_contract.py`.

Validation/resolution remains in `runtime/placement_constraints.py`.

No COLOR, cache/fingerprint, provenance, persistence/database or renderer semantics changed.

## V1.77 rule

Start from the freshly certified V1.76 checkpoint. Re-run the complete read-only responsibility/consumer/contract/impact audit. Do not assume the next seam is placement, visibility, geometry, resolver, appearance, cache, COLOR, persistence or renderer.

The next micro-component requires real owner evidence, real consumer evidence and its own truth dossier with exact line ranges before implementation.
