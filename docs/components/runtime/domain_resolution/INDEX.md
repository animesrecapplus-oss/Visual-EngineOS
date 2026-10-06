# Domain-resolution component dossier — V1.53

## Identity

- Component: `CMP-RUNTIME-DOMAIN-RESOLUTION`
- Semantic path: `runtime/domain_resolution`
- Parent: runtime resolution layer.
- V1.53 scope: one immutable input-contract extraction plus hostile input-boundary hardening.

## Truth files

- `COMPONENT_TRUTH.md` — ownership and boundaries.
- `ROADMAP.md` — remaining work.
- `CONTRACTS.md` — protected input contracts.
- `DEPENDENCIES_AND_CONSUMERS.md` — real graph evidence.
- `INVARIANTS_AND_ASSUMPTIONS.md` — invariants.
- `ADVERSARIAL_TEST_MATRIX.md` — hostile status.
- `TEST_STATUS.md` — executable evidence.
- `DECISIONS.md` — architectural decisions.
- `ERRORS.md` — detected/corrected defects.
- `IMPACT_MAP.md` — V1.53 impact record.
- `EVIDENCE.md` — retained evidence.
- `MANIFEST.json` — traceability registry.

## Owned source

- `domain_input_contract.py` — canonical immutable input envelope and dependency value object.
- `domain_resolution.py` — input factory, unresolved-result factory and compatibility facade.
- `domain_result_contract.py` — canonical immutable result contract from V1.52.
- `domain_result_validation.py` — canonical result-vs-input validation from V1.51.
