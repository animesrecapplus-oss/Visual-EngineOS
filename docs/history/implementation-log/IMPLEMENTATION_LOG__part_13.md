# Implementation log — V1.50

## Architectural immune-system foundation — 2026-09-30

### Formalized protocols

Created `docs/governance/protocols/` with bounded normative documents for global lifecycle, component truth, impact analysis,
hostile review, visual execution, naming/cleanup, traceability IDs and protocol gates.

Created `docs/governance/architecture/COMPONENT_TRUTH_ARCHITECTURE.md` and its index entry.

### Pilot dossier

Created `docs/components/eyes/pupil/`:

- `INDEX.md`
- `COMPONENT_TRUTH.md`
- `ROADMAP.md`
- `CONTRACTS.md`
- `DEPENDENCIES_AND_CONSUMERS.md`
- `INVARIANTS_AND_ASSUMPTIONS.md`
- `ADVERSARIAL_TEST_MATRIX.md`
- `TEST_STATUS.md`
- `DECISIONS.md`
- `ERRORS.md`
- `IMPACT_MAP.md`
- `EVIDENCE.md`
- `MANIFEST.json`

Created mirrored pilot tests under `tests/components/face/eyes/pupil/` and the read-only gate `tools/validate_component_truth.py`.

### Concrete ownership correction

Pilot inspection found `LashShadowSpec` in `pupil/effects.py` while its real semantic consumers were lashes/appearance. The class was moved to
`src/visual_engine/components/face/eyes/lashes/effects.py`. `appearance/spec.py`, `eyes/definitions.py`, `eyes/effects/__init__.py` and `lashes/__init__.py`
were rewired; the public `geometry.LashShadowSpec` identity remains unchanged.

### Source comments

The three pupil implementation files were annotated with explicit ownership/contract/invariant comments on every non-blank code line.
This establishes the strict pilot baseline without retro-commenting unrelated legacy code.

### Evidence and validation

The pilot truth gate passes. Focused pupil/visual compatibility tests pass. `compileall` passes. The architecture graph was rendered to
`artifacts/current/v1.50/V1.50_PUPIL_COMPONENT_TRUTH_GRAPH.png` and visually inspected. The graph is governance evidence, not a rendering-quality claim.

### Current source audit

After the pilot correction: 177 production Python modules, 417 internal import edges, 68 modules above 150 lines and the same three known SCCs.
No new SCC was introduced by the ownership correction.

### Next

V1.51 resumes responsibility-driven modularization, but only after applying the V1.50 protocol gate and writing an impact record first.

## V1.51 completion — domain-result validation extraction

### Audit and selection

Started from the V1.50 certified ZIP. Preflight passed before source edits. Baseline: 177 modules, 417 internal import edges, 68 oversized modules, three known SCCs and zero exact duplicate function groups. `runtime.domain_resolution` was selected because result validation has independent semantics and real BASE/COLOR/MATERIAL consumers.

### Created

- `src/visual_engine/runtime/domain_result_validation.py`;
- V1.51 component truth dossier under `docs/components/runtime/domain_resolution/`;
- `tests/components/runtime/domain_resolution/test_v151_domain_validation_truth.py`;
- `tests/unit/test_v151_architectural_discipline.py`;
- `tools/audit_v151_source_modularization.py`;
- `tools/benchmark_v151_source_modularization.py`;
- `tools/validate_v151_domain_resolution_truth.py`;
- V1.51 contract/report.

### Modified

`domain_resolution.py` retains envelopes/input construction and the compatibility facade. BASE/COLOR/MATERIAL reach the canonical owner through that stable facade; `runtime.__init__` keeps the same public path. Governance architecture/status/roadmap/decision records were updated.

### Hostile correction

The first extraction arrangement created a `domain_resolution ↔ domain_result_validation` cycle. The dependency audit detected it. The validator no longer imports `DomainResolutionStatus` at runtime; the final graph returns to the three pre-existing SCCs.

### Persistence/visual boundary

No persistence module directly imports the selected responsibility. No database schema, migration, cache or fingerprint contract changed. The validator contains no geometry or renderer operation, so independent visual QA is not applicable; production integration remains covered by regression.

### Performance

Five fresh-process runs: V1.50 median-of-medians 18,372.5 ns; V1.51 18,623.5 ns; +1.37%. This is recorded as non-regression within environment variance, not optimization.

Final source ranges, complete regression counts, artifact purge and ZIP hash are finalized in the V1.51 report after source freeze.
