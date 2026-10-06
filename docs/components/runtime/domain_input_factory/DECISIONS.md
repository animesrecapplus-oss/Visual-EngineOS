# Decisions — CMP-DOMAIN-INPUT-FACTORY

## DEC-DIF-001 / D-101 — one-responsibility extraction

Extract only canonical domain-input construction from `domain_resolution.py`.

### Evidence

BASE, COLOR and MATERIAL contain real production factory calls. `unresolved_domain_result` has no production consumer.

### Compatibility

`domain_resolution.build_domain_resolution_input` remains an identity-compatible re-export. `runtime.__init__` exposes the canonical owner.

### Explicit exclusions

No result extraction, no COLOR change, no persistence layer, no cache manager, no renderer work.

## DEC-DIF-002 / D-102 — direct consumer ownership

Real BASE/COLOR/MATERIAL consumers import the canonical factory directly. This proves the owner is not merely a relocated implementation hidden behind the facade.
