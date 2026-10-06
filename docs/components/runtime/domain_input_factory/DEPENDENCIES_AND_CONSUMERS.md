# Dependencies and consumers — CMP-DOMAIN-INPUT-FACTORY

## Real production consumers

- `CON-DIF-001` — `runtime.base_resolution:176,207` builds BASE inputs.
- `CON-DIF-002` — `runtime.color_resolution:22` imports the canonical factory for COLOR input construction.
- `CON-DIF-003` — `runtime.material_resolution:138` builds MATERIAL inputs.
- `CON-DIF-004` — `runtime.__init__:151` exposes the canonical public factory.
- `CON-DIF-005` — `runtime.domain_resolution:42` preserves the historical compatibility symbol.

## Dependencies

- `appearance_contract` — domain/contribution contracts.
- `domain_input_contract` — immutable value-object owner.
- `domain_result_contract` — existing rendering-domain guard.
- lazy `appearance_role_bridge` import only when a typed role is supplied.

## Boundaries

No persistence/database module imports the factory. No ResolutionCache or renderer module imports it. No new COLOR semantics are introduced.

## Evidence

`REL-DIF-001` confirms one-way ownership: consumers → factory → input contract; the factory does not import the legacy facade.
