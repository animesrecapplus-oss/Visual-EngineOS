# Impact map

`IMP-RC-001` source: `runtime.contract` loses only the `ResolutionContext` contract and retains resolution/result ownership.

`IMP-RC-002` consumers: production modules move to the canonical owner; compatibility import remains available.

`IMP-RC-003` cache/fingerprint: `context_fingerprint`, `resolution_fingerprint` and cache implementation are unchanged.

`IMP-RC-004` persistence/database: no consumer, SQL, migration or serialization path touched.

`IMP-RC-005` COLOR: no new downstream COLOR consumer and no COLOR algorithm change.

`IMP-RC-006` determinism: canonical ordering and legacy-shadow semantics are preserved by focused tests and production identity.

`IMP-RC-007` parent/children/siblings: generic resolver, state/effect policy, production request path and style path remain semantically unchanged.

`IMP-RC-008` visual: selected seam contains no renderer operation; nevertheless real production SVG/camera/visibility identity is checked against V1.67.

`IMP-RC-009` line budget: new owner is 97 lines; modified oversized legacy modules remain explicit debt and receive no unrelated refactor.
