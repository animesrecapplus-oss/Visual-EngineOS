# Relations

Parent semantic path: `runtime.contract.resolve_component` consumes `ResolutionContext`.

Children: none.

Siblings: `state_policy`, `effects`, `versioning`, `resolution_cache`, `production_face_render`, `production_visual_styles`.

`REL-RC-001`: `ResolutionContext → state_policy` is input typing only; precedence remains downstream.

`REL-RC-002`: `ResolutionContext → effects` is input typing plus legacy-shadow construction; composition remains downstream.

`REL-RC-003`: `ResolutionContext → versioning` is consumer-only; fingerprint ownership remains in `versioning`.

`REL-RC-004`: `ResolutionContext → production` is dependency injection of an immutable request input.

`REL-RC-005`: `runtime.contract → resolution_context` is one-way compatibility re-export; reverse dependency is forbidden.
