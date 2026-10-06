# Domain-resolution decisions — V1.53

## DEC-DOMAIN-009 / D-099 — input-envelope ownership boundary — 2026-09-30

### Decision

Extract exactly one responsibility from `runtime.domain_resolution`: the immutable domain-input contract. The canonical
owner is `runtime.domain_input_contract`.

### Included

- `DomainDependency`;
- `DomainResolutionInput`;
- their construction-time invariants and deterministic input digest.

### Excluded

`build_domain_resolution_input`, `unresolved_domain_result`, domain algorithms, result validation, persistence, cache
ownership, fingerprints and rendering remain in existing owners.

### Compatibility

`runtime.domain_resolution` re-exports the moved input symbols. Existing BASE/COLOR/MATERIAL imports and
`runtime.__init__` exports remain valid and identity-compatible.

### Safety constraints

The new owner must not import `domain_resolution`. Constructor hardening may reject impossible runtime types, but valid
input values and digest semantics must remain unchanged. No COLOR implementation changes.

## DEC-DOMAIN-010 / D-100 — hostile input-boundary hardening — 2026-09-30

The selected owner explicitly rejects invalid domain, target/resolver identity, contribution and dependency runtime
containers, plus non-canonical state/dependency ordering. This closes impossible API states without adding domain
semantics.
