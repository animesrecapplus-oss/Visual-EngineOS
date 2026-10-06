# Contracts — CMP-DOMAIN-INPUT-FACTORY

## CON-DIF-001 — canonical construction

Every returned value is an instance of the canonical `DomainResolutionInput` owner.

## CON-DIF-002 — domain admission

The factory uses the existing rendering-domain guard and adds no domain semantics.

## CON-DIF-003 — dependency canonicalization

Mapping inputs become `DomainDependency` values sorted by name. Tuple inputs must contain only `DomainDependency` values and are sorted by name.

## CON-DIF-004 — typed-role dependency

A typed role contributes the `appearance_role_bridge` fingerprint as a dependency; contradictory existing identity is rejected.

## CON-DIF-005 — state canonicalization

Active states are converted to sorted unique tuples before the immutable contract is constructed.

## CON-DIF-006 — compatibility

The historical facade and public runtime export resolve to the same factory function object.
