# Domain-resolution impact record — V1.53

## IMP-V1.53-001 — pre-change selection

- Audited owner: `runtime.domain_resolution` at the certified V1.52 checkpoint.
- Selected responsibility: immutable domain-input envelope plus dependency value object.
- Canonical target: `runtime.domain_input_contract`.
- Compatibility surface: `runtime.domain_resolution` re-exports the moved symbols and retains the factory.

## Consumers

BASE, COLOR and MATERIAL resolvers consume the input type through the historical facade. `runtime.__init__` exposes
that facade. No production consumer imports the new owner before V1.53.

## Contract / invariant impact

Preserve field order, defaults, equality/frozen semantics, contribution/state/dependency canonicalization, role-bridge
rules and `input_digest`. Historical imports must resolve to the same class objects.

## Cache / fingerprint / provenance

No ResolutionCache or ResolutionFingerprint code is changed. The input digest remains the same stable-digest operation;
no cache identity is intentionally altered. Role contribution fingerprint and dependency identity remain part of the input.

## Persistence / database

Repository search found zero direct persistence consumers and zero database migrations related to this contract. No DB
change is justified.

## Determinism / visual impact

The seam contains no geometry or renderer operation. No visual behavior is intentionally changed; a new PNG/SVG would
be fabricated evidence. Existing production render tests remain mandatory.

## Required unchanged behavior

- legacy imports remain identity-compatible;
- BASE/COLOR/MATERIAL outputs remain unchanged for valid inputs;
- no COLOR semantic implementation changes;
- no persistence behavior changes;
- no new dependency SCC;
- no second extraction in V1.53.
