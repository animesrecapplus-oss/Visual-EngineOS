# Current status — V1.54

## V1.54 canonical domain-input factory

V1.54 is the current source-modularization checkpoint. It starts from certified V1.53 and extracts exactly one responsibility from `runtime.domain_resolution`: canonical construction and normalization of `DomainResolutionInput`.

### Current owner

`src/visual_engine/runtime/domain_input_factory.py`, lines 1–64.

### Production consumers

- BASE: `runtime/base_resolution.py:176,207`.
- COLOR: `runtime/color_resolution.py:22`.
- MATERIAL: `runtime/material_resolution.py:138`.
- Public runtime export: `runtime/__init__.py:151`.
- Historical compatibility: `runtime/domain_resolution.py:42`.

### Boundaries

The factory does not own the immutable input value object, result construction/validation, domain algorithms, cache/fingerprint lifecycle, persistence, geometry, visibility or rendering.

`unresolved_domain_result()` remains in `domain_resolution.py` because no production consumer proves an independent owner boundary.

### Verification

- Component truth gate: PASS.
- Full deterministic matrix: 125 test files / 1023 tests / 1022 passed / 1 expected PostgreSQL skip / 0 failed.
- Compileall: PASS.
- Dependency graph: 181 modules / 435 internal edges / 3 pre-existing SCCs.
- Exact duplicate groups: 0.
- Persistence direct consumer: false.
- COLOR semantic change: false.
- Visual QA: NOT_APPLICABLE.

### Performance

Fresh-process median-of-medians versus V1.53: construction `4868.0 → 3746.0 ns` (-23.048%); input digest `15693.0 → 8002.0 ns` (-49.009%). No optimization was introduced.

### Artifact policy

Only `artifacts/current/v1.54/` is retained as generated current evidence. The V1.53 current evidence was purged; historical documentation remains provenance.
