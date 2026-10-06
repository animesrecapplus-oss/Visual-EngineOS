# Invariants and assumptions — CMP-DOMAIN-INPUT-FACTORY

## Invariants

- exactly one canonical factory implementation exists;
- factory never imports the legacy facade;
- output type is `DomainResolutionInput`;
- dependency names are canonicalized by the value-object contract;
- typed-role dependency identity cannot silently conflict;
- active states are sorted and deduplicated;
- no result or renderer behavior is produced by the factory.

## Assumptions

- `DomainResolutionInput` remains the canonical immutable owner;
- existing contribution and role contracts remain authoritative;
- `stable_digest` semantics remain downstream of the input contract;
- callers accept canonical ordering rather than preserving input ordering.

## Persistence assumption

No database record currently depends directly on this factory. A future persistence consumer must receive its own explicit contract before adoption.
