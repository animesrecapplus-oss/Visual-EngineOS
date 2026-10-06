# Guarantees and status — CMP-PCOV-001

## Guarantees

- One canonical `CoverageIntent` owner.
- Deterministic uniform-scale coverage resolution.
- Explicit failure for invalid numeric/type/geometry preconditions.
- No object-specific rules.
- No cache/fingerprint/provenance/persistence/COLOR side effects.
- Historical public identity preserved.

## Status

`CERTIFIED`: component gate, 1144-test regression (1143 passed + 1 expected PostgreSQL skip), compileall, graph/cycle/duplicate audit, benchmark, visual QA, documentation, purge and ZIP integrity have PASS evidence.
