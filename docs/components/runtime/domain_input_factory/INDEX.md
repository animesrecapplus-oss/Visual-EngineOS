# CMP-DOMAIN-INPUT-FACTORY — truth index

- `CMP-DOMAIN-INPUT-FACTORY` — canonical construction/normalization micro-component.
- Owner: `src/visual_engine/runtime/domain_input_factory.py`, lines 1–64.
- Parent: generic runtime domain-resolution layer.
- Siblings: `domain_input_contract`, `domain_result_contract`, `domain_result_validation`, BASE/COLOR/MATERIAL resolvers.
- Compatibility facade: `domain_resolution.py`, lines 42–58.
- Production consumer imports: BASE lines 176/207; COLOR line 22; MATERIAL line 138; public runtime line 151.
- Status: `IMPLEMENTED / INTEGRATED / HOSTILE_VALIDATED` after V1.54 certification.
- Visual QA: `NOT_APPLICABLE` because no rendering responsibility is owned here.
- Persistence: no direct consumer; no database change.
- Evidence IDs: `EVD-DIF-001..007`.
