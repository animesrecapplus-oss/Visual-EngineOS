# Refactor records

- `V1.48_SOURCE_MODULARIZATION_CONTRACT.md` — source-code extraction rules and selected seam.
- `V1.48_SOURCE_MODULARIZATION_REPORT.md` — audit, dependency graph, duplicate analysis, tests and benchmark.
- `ARTIFACT_RETENTION_POLICY.md` — current-only generated-evidence policy; the `artifacts/` directory itself is retained.
- `FILE_PLACEMENT_POLICY.md` — documentation placement rules.
- `MIGRATION_MAP_01.md` / `MIGRATION_MAP_02.md` — V1.47 documentation migration records.

## V1.48 source audit

- 174 production Python modules audited.
- 67 modules exceed 150 lines; none are split solely because of that count.
- 408 direct import edges; no multi-module cycle detected.
- 0 exact duplicate function-body groups.
- One 97.9% similarity candidate was manually rejected as a domain-contract false positive.
- One responsibility extracted from `runtime.visibility` into `runtime.region_geometry`.
- Public runtime import identities preserved.
- The `artifacts/` directory remains; only the latest certified brick's evidence is retained under `artifacts/current/vX.Y/`.

## V1.50 architectural discipline

- `V1.50_ARCHITECTURAL_DISCIPLINE_CONTRACT.md` — normative architectural immune-system contract.
- `V1.50_ARCHITECTURAL_DISCIPLINE_REPORT.md` — formalization, pilot, ownership correction, validation and next gate.
- `docs/governance/protocols/` — mandatory lifecycle, truth, impact, hostile, visual, naming, traceability and certification protocols.
- First pilot: `CMP-EYE-PUPIL`; no broad repository migration.
- `LashShadowSpec` ownership corrected from pupil to lashes with legacy API identity preserved.

## V1.51 source modularization

- `V1.51_SOURCE_MODULARIZATION_CONTRACT.md` — selected responsibility and mandatory guarantees.
- `V1.51_SOURCE_MODULARIZATION_REPORT.md` — audit, impact, extraction, hostile review, integration and certification record.
- Runtime component truth: `docs/components/runtime/domain_resolution/`.

## V1.52 source modularization

- `V1.52_SOURCE_MODULARIZATION_CONTRACT.md` — selected result-contract responsibility and guarantees.
- `V1.52_SOURCE_MODULARIZATION_REPORT.md` — audit, impact, hostile testing, integration, benchmark and certification record.

## V1.53 source modularization

- `V1.53_SOURCE_MODULARIZATION_CONTRACT.md` — selected immutable input-contract responsibility and guarantees.
- `V1.53_SOURCE_MODULARIZATION_REPORT.md` — verify, architect, impact, implementation, hostile review, integration, benchmark, purge and certification record.
- Runtime component truth remains under `docs/components/runtime/domain_resolution/`.

- `V1.57_HAIR_PRODUCTION_REPORT.md` / `V1.57_HAIR_PRODUCTION_CONTRACT.md` — Hair production boundary and evidence.

## V1.58 Hair/Ear occlusion

- `V1.58_HAIR_EAR_OCCLUSION_CONTRACT.md` — bounded interaction contract.
- `V1.58_HAIR_EAR_OCCLUSION_REPORT.md` — twelve-step audit, implementation, hostile review, visual evidence and certification record.
- `docs/components/face/hair_depth/` — dedicated Hair depth micro-component truth dossier.
- `docs/components/face/production_hair_ear_occlusion/` — dedicated production occlusion micro-component truth dossier.
## V1.71 source modularization

- `V1.71_SOURCE_MODULARIZATION_CONTRACT.md` — bounded ProductionRenderSession lifecycle extraction and certification guarantees.
- `docs/components/runtime/production_render_session/` — dedicated micro-component truth dossier.
