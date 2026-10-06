# Roadmap — V1.77 and next frontier

## V1.77 — Placement contract ownership extraction

Fresh V1.76 audit selected immutable placement vocabulary, intent and solution contracts as a distinct responsibility inside `runtime.placement`.

Owner: `runtime/placement_contract.py`.

Placement solving and geometry materialization remain in `runtime/placement.py`.

No COLOR, cache/fingerprint, provenance, persistence/database or renderer semantics changed.

## V1.78 rule

Start from the freshly certified V1.77 checkpoint. Re-run the complete read-only responsibility/consumer/contract/impact audit. Do not assume the next seam is placement, visibility, geometry, resolver, appearance, cache, COLOR, persistence or renderer.

The next micro-component requires real owner evidence, real consumer evidence and its own truth dossier with exact line ranges before implementation.
