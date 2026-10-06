# Domain-resolution dependencies and consumers — V1.53

## Production consumers

| Consumer | Real use |
|---|---|
| `runtime.base_resolution` | receives `DomainResolutionInput` through the compatibility factory |
| `runtime.color_resolution` | receives `DomainResolutionInput` through the compatibility factory |
| `runtime.material_resolution` | receives `DomainResolutionInput` through the compatibility factory |
| `runtime.__init__` | exposes historical input/dependency symbols |
| `runtime.domain_resolution` | compatibility facade and canonical factory owner |

## Canonical input-owner dependencies

- `appearance_contract` — contribution/domain contracts and contribution validation.
- `domain_result_contract` — canonical renderable-domain and digest guards.
- `versioning` — deterministic `stable_digest`.
- `appearance_role_bridge` is imported lazily only for the runtime type boundary of the optional role contribution.

## Persistence / cache / renderer

A repository search found no persistence/database consumer of `DomainResolutionInput`, `DomainDependency` or the new
owner. No database migration is justified. ResolutionCache and ResolutionFingerprint do not directly consume the input
contract. Renderer/geometry/visibility packages do not import the selected owner.

## Relations

Parent: runtime resolution layer. Siblings: BASE/COLOR/MATERIAL resolvers, result contract and result validation.
The selected owner is a leaf semantic input contract and does not import the legacy facade.
