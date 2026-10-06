# Component truth — CMP-PCOV-001

## Identity

`CMP-PCOV-001` — `runtime/placement_coverage` — V1.74.

## Parent / children / siblings

- Parent: generic runtime spatial placement.
- Children: none; the coverage contract and numerical solver are one bounded responsibility.
- Siblings: `runtime.placement_constraints`, `runtime.spatial_relationships`, `runtime.placement_visibility`.

## Responsibility

`CoverageIntent` validates the coverage request. `resolve_coverage_scale` resolves the deterministic uniform scale against two positive-area regions using the existing anchor-centered placement semantics.

## Non-responsibility

General anchors/dimensions/rotation/depth; relation compilation; hard constraints; visibility/occlusion; geometry transforms; renderer; COLOR; cache/fingerprint/provenance; persistence/database; request/session lifetime.

## Owner

`FILE-PCOV-001`: `src/visual_engine/runtime/placement_coverage.py`.
