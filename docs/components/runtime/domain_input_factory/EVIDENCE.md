# Evidence — CMP-DOMAIN-INPUT-FACTORY

## Evidence IDs

- `EVD-DIF-001` — pre-change responsibility/consumer audit.
- `EVD-DIF-002` — component truth gate.
- `EVD-DIF-003` — hostile/API compatibility tests.
- `EVD-DIF-004` — dependency/cycle/duplicate audit.
- `EVD-DIF-005` — fresh-process benchmark.
- `EVD-DIF-006` — deterministic full test matrix.
- `EVD-DIF-007` — artifact retention and ZIP integrity.

## Exact evidence files

- `artifacts/current/v1.54/V1.54_SOURCE_AUDIT.json`
- `artifacts/current/v1.54/V1.54_BENCHMARK.json`
- `artifacts/current/v1.54/V1.54_VALIDATION_MANIFEST.json`
- `artifacts/current/v1.54/V1.54_COMPONENT_GATE.json`
- `artifacts/current/v1.54/V1.54_SOURCE_DELTA.json`
- `artifacts/current/v1.54/V1.54_RELEASE_EVIDENCE.txt`
- `artifacts/current/v1.54/V1.54_ARTIFACT_SHA256.txt`

## Visual scope

`NOT_APPLICABLE`: no geometry, visibility, camera or renderer operation is owned here.

## Persistence boundary

`persistence_direct_consumer=false`; live PostgreSQL is not claimed without its configured DSN.

## Status rule

Only completed executable evidence can promote a gate to PASS.
