# Prechange impact audit — CMP-PCOV-001

`EVD-PCOV-001` records the fresh V1.73 read-only audit.

Selected responsibility: coverage-specific immutable request contract plus deterministic uniform-scale solver inside `runtime.placement`.

Real consumers proven before change: `runtime.placement.resolve_placement` and `runtime.spatial_relationships.compile_relation_placement`; public export was also traced.

Affected source: `placement.py`, `spatial_relationships.py`, `runtime/__init__.py`, plus one new canonical owner and dedicated truth tests.

Frozen: non-coverage placement semantics, relation semantics, visibility, renderer, COLOR, cache/fingerprint/provenance, persistence/database and production session lifecycle.

Visual impact is applicable because placement can reach rendering; therefore production normal/boundary/interaction evidence is mandatory.
