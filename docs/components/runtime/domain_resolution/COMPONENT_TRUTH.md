# Domain-resolution component truth — V1.53

## Responsibility

The component owns renderer-neutral domain-resolution envelopes. V1.53 gives the immutable input envelope and
`DomainDependency` one canonical owner; input construction remains a compatibility factory in `domain_resolution`.
Result types and result validation remain in their V1.52/V1.51 owners.

## Non-responsibilities

It does not run BASE/COLOR/MATERIAL algorithms, persist records, own resolution caches/fingerprints, render geometry,
perform camera work, or decide visual quality.

## Owners

- `runtime.domain_input_contract` — canonical input envelope and dependency value object.
- `runtime.domain_resolution` — input factory, unresolved-result factory and compatibility facade.
- `runtime.domain_result_contract` — canonical result envelope.
- `runtime.domain_result_validation` — canonical result/input semantic validation.

## Guarantees

Input identity is immutable and deterministic. Contributions, states, dependencies, resolver identity and optional
role contribution are validated at construction. Historical imports remain object-identity compatible.

## Status

`IMPLEMENTED / INTEGRATED / HOSTILE_VALIDATED`. No unresolved responsibility is promoted without a fresh audit.
