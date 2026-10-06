# Decision register — V1.74

`D-160` — Select `CMP-RUNTIME-PLACEMENT-COVERAGE` because coverage request validation and geometric uniform-scale solving form one bounded responsibility inside `runtime.placement`, with real consumers.

`D-161` — Move `CoverageIntent` and coverage numerical helpers only; keep general placement anchors, dimensions, rotation, depth, `PlacementSolution` and relation-local geometry materialization in their existing owners.

`D-162` — Make `runtime.placement_coverage` the canonical public contract owner while preserving historical `runtime.placement.CoverageIntent` identity.

`D-163` — Reject direct-solver non-finite/type-invalid inputs before Shapely; hostile evidence proved that relying on downstream geometry errors was too permissive.

`D-164` — Freeze cache/fingerprint/provenance, persistence/database, COLOR, visibility and renderer semantics because no real downstream consumer requires a change.
