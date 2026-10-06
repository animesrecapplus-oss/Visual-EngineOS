# Decisions

`DEC-POG-001`: V1.62 extracts only the existing owner-geometry selection/rebasing responsibility from `production_slice.py`.
`DEC-POG-002`: the existing semantics are preserved rather than redesigning geometry metadata.
`DEC-POG-003`: one canonical callable replaces the old private helper; no duplicate helper remains in `production_slice.py`.
`DEC-POG-004`: the callable is exported from `visual_engine.runtime` because three real production interaction paths depend on this boundary.
`DEC-POG-005`: no COLOR, database, cache-lifetime, fingerprint or renderer algorithm change is authorized.
`DEC-POG-006`: exact V1.61→V1.62 SVG/result identity is a hard gate.
