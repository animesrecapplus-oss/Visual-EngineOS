# Relations

Parent semantic path: `runtime.contract.resolve_component` produces `ResolvedComponent`.

Children: none. `ResolutionTrace` is a value sub-contract of the result envelope, not a second production owner.

Siblings: `resolution_context`, `provenance`, `versioning`, `resolution_cache`, `production_face_render`.

`REL-RCMP-001`: resolver → result is construction only; resolution policy remains in `runtime.contract`.

`REL-RCMP-002`: result → provenance/version/fingerprint is typed composition; those modules retain ownership.

`REL-RCMP-003`: result → production is output consumption; production does not reconstruct the result.

`REL-RCMP-004`: `runtime.contract → resolved_component` is one-way canonical import plus compatibility re-export.
Reverse dependency is forbidden.
