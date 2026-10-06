# Relations — CMP-PCOV-001

- `REL-PCOV-001`: `runtime.placement → placement_coverage`; contract: `CoverageIntent` + scale tuple; invariant: coverage remains uniform and deterministic; tests: V1.74 truth + V1.3 placement.
- `REL-PCOV-002`: `runtime.spatial_relationships → placement_coverage`; contract: canonical `CoverageIntent`; invariant: relation metadata compiles without duplicate contract; tests: spatial placement regression.
- `REL-PCOV-003`: `runtime.__init__ → placement_coverage`; contract: public `CoverageIntent`; invariant: object identity preserved; test `TST-PCOV-001`.
- `REL-PCOV-004`: `placement_coverage → Shapely`; contract: finite geometric operations only; invariant: invalid numerics rejected first; adversarial tests `ADV-PCOV-001..008`.
- `REL-PCOV-005`: production placement → render; contract: `PlacementSolution`; invariant: output unchanged by extraction; visual evidence `EVD-PCOV-007..010`.
