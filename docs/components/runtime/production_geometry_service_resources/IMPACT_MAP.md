# Impact map

`IMP-GSR-001` direct: `production_render_session.py` construction/use/close of the geometry service remains the session lifecycle boundary.

`IMP-GSR-002` relational: existing session cache ownership contracts must remain byte/semantically unchanged.

`IMP-GSR-003` sibling: visual styles, owner geometry and relation adapters remain untouched semantically.

`IMP-GSR-004` transverse cache/fingerprint: supplied `GeometryCache` identity and policy are unchanged; no new cache owner.

`IMP-GSR-005` persistence/database: no production persistence or SQL path is referenced.

`IMP-GSR-006` COLOR: no COLOR consumer or transformation is introduced.

`IMP-GSR-007` determinism: registry construction and service binding remain deterministic.

`IMP-GSR-008` visual: production SVG must remain byte-identical to the V1.65 five-case baseline.
