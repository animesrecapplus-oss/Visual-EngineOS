# Domain-resolution contracts — V1.53

## CON-DOMAIN-008 — input identity

`DomainResolutionInput` targets exactly one renderable `AppearanceDomain` and carries non-empty resolver and contract
identity strings.

## CON-DOMAIN-009 — contribution boundary

Every contribution is an `AppearanceContribution`, belongs to the input domain, and has a unique contribution ID.

## CON-DOMAIN-010 — state canonicalization

`active_states` is a tuple of non-empty strings already sorted and deduplicated.

## CON-DOMAIN-011 — dependency identity

Every dependency is a `DomainDependency` with a non-empty name and SHA-256 digest; dependency names are unique and
stored in canonical name order.

## CON-DOMAIN-012 — typed-role authority

A typed role contribution must target the same component, is legal only for BASE/COLOR, and cannot coexist with a
legacy contribution for that same domain.

## CON-DOMAIN-013 — deterministic input digest

`input_digest` is the stable digest of the complete immutable input envelope. Geometry is not an implicit dependency.
