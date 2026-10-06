# File placement policy

## Documentation

- `docs/governance/` — authoritative system-wide contracts and navigation.
- `docs/components/` — component and micro-component contracts.
- `docs/runtime/` — generic runtime contracts.
- `docs/domains/` — domain-specific contracts such as COLOR.
- `docs/history/` — immutable historical reports and superseded architecture records.
- `docs/refactor/` — structural audits and migration records only.

## Evidence

- `artifacts/releases/vX.Y/manifest.json` — release manifest for that checkpoint.
- `artifacts/releases/vX.Y/evidence/` — release evidence for that checkpoint.
- `artifacts/current/vX.Y/` — current active evidence only.
- `artifacts/history/vX.Y/` — retained historical evidence.

## Repository root

The root is reserved for the project README, build metadata and source-control metadata. Release evidence, manifests, test matrices and generated visual boards do not belong here.
