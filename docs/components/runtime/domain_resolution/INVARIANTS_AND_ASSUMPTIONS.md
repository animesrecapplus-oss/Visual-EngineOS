# Domain-resolution invariants and assumptions — V1.53

## Invariants

- Input target ID is a non-empty string.
- Input domain is an `AppearanceDomain` admitted by the canonical rendering-domain guard.
- Resolver ID, resolver version and contract version are non-empty strings.
- Contributions are typed, same-domain and uniquely identified.
- Active states are canonical sorted unique non-empty strings.
- Dependencies are typed, uniquely named and sorted by name.
- Dependency digests are valid SHA-256 identities.
- Optional role contribution targets the input target and cannot create a second authority.
- Input value is immutable and `input_digest` is deterministic.

## Assumptions

- `DOMAIN_CONTRACTS` remains the semantic field registry.
- `stable_digest` remains deterministic and canonical.
- Existing production callers use the declared value-object forms.

## Interaction boundary

The input contract does not decide result status, domain output fields, geometry, occlusion, visibility or renderer
behavior. Those remain separate owners and are regression-tested at their own boundaries.
