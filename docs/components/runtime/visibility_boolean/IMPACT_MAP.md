# Impact map — CMP-VBOOL-001

- `IMP-VBOOL-001` source: `visibility.py`, new `visibility_boolean.py`, `runtime/__init__.py`.
- `IMP-VBOOL-002` consumers: compatibility facade, package API and visibility-kernel tests.
- `IMP-VBOOL-003` parent/siblings: visibility, region geometry, coverage, attribution.
- `IMP-VBOOL-004` contracts: boolean API identity/result semantics preserved.
- `IMP-VBOOL-005` cache/fingerprint/provenance: no change.
- `IMP-VBOOL-006` persistence/database: no placement/visibility schema consumer found; no migration changed.
- `IMP-VBOOL-007` determinism: repeated boolean and production render outputs match V1.74.
- `IMP-VBOOL-008` visual behavior: production SVG/camera hashes match V1.74 for normal, ±30° and zoom interaction cases.
