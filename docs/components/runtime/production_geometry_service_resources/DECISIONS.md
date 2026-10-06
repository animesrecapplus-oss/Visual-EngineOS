# Decisions

`DEC-GSR-001`: select the existing registry/service lifecycle seam because it is an independent real
responsibility inside the production session.

`DEC-GSR-002`: do not move cache construction or ownership. Historical V1.45/V1.46 tests explicitly
identify the production session as the `ResolutionCache` owner; V1.71 moves that already-established session ownership from `production_slice.py` into the canonical session owner, while a hostile full-regression batch
caught this boundary when the first broader resource extraction moved cache construction.

`DEC-GSR-003`: the final owner receives an already-created `GeometryCache` and never clears it.

`DEC-GSR-004`: do not export the new micro-component through `runtime.__init__`; it is an internal owner,
not a new public API.

`DEC-GSR-005`: preserve the existing generation service and registry exactly; no algorithmic refactor is bundled.
