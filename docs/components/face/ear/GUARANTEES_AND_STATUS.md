# Guarantees and status — CMP-FACE-EAR

## Guarantees

- `CON-FE-004`: output remains a renderer-neutral `GeometryContract`.
- `INV-FE-001`: finite geometry is enforced by the shared contract.
- `INV-FE-006`: malformed width/height values cannot be silently coerced into geometry.
- Cache identity changes when authored valid ear geometry changes through the existing generation path.

## Status

`V1.80 / CERTIFIED`: the existing Ear production micro-component passed its component gate, hostile tests, integration suite, full regression, compileall, dependency graph review, benchmark, visual invariance check, documentation validation, purge and ZIP integrity.
