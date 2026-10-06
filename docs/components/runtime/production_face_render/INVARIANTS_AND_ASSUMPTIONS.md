# Invariants and assumptions

`INV-PFR-001`: the session remains the sole production owner of graph/cache lifetime.

`INV-PFR-002`: injected caches are never cleared by the render owner.

`INV-PFR-003`: one request uses the supplied graph, version, context and resolution cache consistently.

`INV-PFR-004`: the root visual already returned by generic resolution is reused by the style owner; no duplicate root resolution is added.

`INV-PFR-005`: geometry, transform, style, renderer and relation calls remain in the same semantic order as V1.66.

`INV-PFR-006`: unknown relation mappings do not gain proof through this orchestration layer.

`INV-PFR-007`: returned result contains no session/graph/cache/resource references.

`INV-PFR-008`: deterministic inputs produce the same SVG/result evidence as the V1.66 production path.
