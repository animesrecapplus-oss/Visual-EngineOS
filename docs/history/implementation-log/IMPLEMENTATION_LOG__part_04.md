<!-- Refactored from ['docs/history/implementation-log/IMPLEMENTATION_LOG__part_01.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_02.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_03.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_04.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_05.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_06.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_07.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_08.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_09.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_10.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_11.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_12.md']; source lines 420-557; content preserved. -->
<!-- Part 4/12. Use the family index for navigation. -->
## Files modified

- `src/visual_engine/runtime/domain_resolution.py`
- `src/visual_engine/runtime/base_resolution.py`
- `src/visual_engine/runtime/version_policy.py`
- `src/visual_engine/runtime/__init__.py`
- `tools/verify_a4_docs.py`
- `tools/verify_a10_full_audit.py`
- `docs/governance/status/CURRENT_STATUS__part_01.md`
- `docs/governance/roadmap/ROADMAP__part_01.md`
- `docs/governance/architecture/ENGINE_VISION__part_01.md`
- `docs/governance/decisions/DECISIONS__part_01.md`
- `docs/history/implementation-log/IMPLEMENTATION_LOG__part_01.md` (split document; see adjacent parts)
- `artifacts/current_test_matrix/REPORT.json`

## Removed from current checkpoint

- `artifacts/v128_appearance_role_bridge/` — superseded working artifact directory. The V1.28 historical
  report remains as provenance, but the current V1.29 checkpoint does not carry the stale previous-brick board.

## Exact line snapshot

Final line counts after implementation and source freeze:

- `src/visual_engine/runtime/typed_appearance_input.py`: 154 lines (new)
- `src/visual_engine/runtime/domain_resolution.py`: 379 lines
- `src/visual_engine/runtime/base_resolution.py`: 205 lines
- `src/visual_engine/runtime/version_policy.py`: 34 lines
- `src/visual_engine/runtime/__init__.py`: 217 lines
- `tests/unit/test_v129_typed_appearance_input.py`: 213 lines (new)
- `tools/visual_qa_v129_typed_appearance_input.py`: 154 lines (new)
- `tools/verify_v129_typed_appearance_input.py`: 83 lines (new)
- `docs/domains/color/V1.29_TYPED_APPEARANCE_INPUT_CONTRACT.md`: 99 lines (new)
- `docs/governance/status/CURRENT_STATUS__part_01.md`: 101 lines
- `docs/governance/roadmap/ROADMAP__part_01.md`: 1556 lines
- `docs/governance/architecture/ENGINE_VISION__part_01.md`: 1053 lines
- `docs/governance/decisions/DECISIONS__part_01.md`: 1094 lines
- `docs/history/implementation-log/IMPLEMENTATION_LOG__part_01.md` (split document; see adjacent parts): 1539 lines after this snapshot entry
- `tools/verify_a4_docs.py`: 92 lines
- `tools/verify_a10_full_audit.py`: 272 lines
- `artifacts/current_test_matrix/REPORT.json`: 15 lines

Affected ranges are documented as concrete implementation blocks: typed envelope 1–154; domain provenance/input/factory/validation 19–22, 85–181, 238–340; BASE typed resolver/factory 32–155; exports 145–217; version policy 20–22; and the V1.29 test/visual/verifier modules are entirely new.

## Explicit nonclaims

- LIVE_POSTGRES = UNVERIFIED
- PACKAGE_BUILD = NOT VERIFIED unless the current environment supplies the build backend
- PRODUCTION_ART_QUALITY = NOT CLAIMED
- No lighting, shading, BRDF, metallic/roughness response, transmission compositing, reflection, style response,
  gamut mapping or renderer-specific post-processing was added.

## Next step — V1.30 micro-scope

1. audit every remaining consumer of `AppearanceResolutionInput.base_color`;
2. classify each consumer as legacy compatibility, genuine BASE consumer, or future COLOR consumer;
3. migrate only genuine BASE consumers to `TypedAppearanceInput`/typed role data;
4. preserve exact authored/generated semantics and provenance;
5. extend typed role provenance to the first actual COLOR-domain consumer only when that domain has a declared
   non-mixing contract;
6. add invalidation tests proving BASE changes do not invalidate geometry and unrelated sibling changes do not
   invalidate typed appearance;
7. render before/after visual samples for migrated generic object/hand/plant paths and reject any semantic or visual drift;
8. only then decide whether `AppearanceResolutionInput.base_color` can become deprecated rather than merely compatible.

No lighting/shading/BRDF/material-physics feature belongs in V1.30 unless a separate contract explicitly requires it.

# V1.30 — Typed BASE Consumer Migration — 2026-09-23

## Objective

V1.30 closes the internal consumer gap left after V1.29. The selected
`AppearanceRoleContribution` and `TypedAppearanceInput` were already canonical,
but the repository still needed a mechanically enforced rule that internal BASE
domain consumers must use the typed path rather than rebuilding the legacy
`AppearanceResolutionInput.base_color` representation.

## Implementation

1. Audited every `build_appearance_input(` occurrence under `src/`.
2. Confirmed the only permitted source occurrences are the compatibility API
definition, the role bridge, and the explicit typed-to-legacy escape hatch.
3. Added `TypedAppearanceInput.to_base_domain_input()` as the direct typed BASE
consumer seam.
4. Added `build_base_resolution_input_from_typed()` and
`resolve_base_domain_from_typed()`; both forward the typed role unchanged.
5. Added V1.30 static source audit `verify_v130_legacy_consumer_migration.py`.
6. Added adversarial migration tests covering authority duplication, tampering,
dependency contradiction, geometry independence, sibling independence and
Palette-selected roles.
7. Added visual QA using actual typed and compatibility resolver outputs for
object, hand, plant and Palette-selected hand paths.
8. Bumped engine/package version 1.3.5 → 1.3.6 and resolution identity 15 → 16.

## Self-critique / corrections

The first test draft used a non-existent `runtime.runtime_graph` import and was
corrected to the canonical `runtime.graph` module. A second draft assumed a
`BaseColorRole.BASE` member; repository inspection showed the actual semantic
roles and the test was corrected to `PRIMARY`. A compatibility comparison initially
mistook authored sRGB case preservation for a semantic difference; the comparison
was corrected to preserve authored spelling while comparing canonical resolver
output semantically. A tampering test that tried to violate the role's own authored
representation invariant was replaced by a direct role-fingerprint tamper test,
so the test exercises the intended boundary rather than a lower-level unrelated
failure.

## Visual QA

Generated and manually inspected:

`artifacts/v130_legacy_consumer_migration/V1.30_TYPED_VS_LEGACY_MIGRATION.png`

The board shows actual semantic outputs, not fabricated colors. The alpha-bearing
sample is composited on white for display only; no opacity is silently converted to
opaque data in the runtime. The diagnostic geometry is deliberately simple and is
not presented as production artwork.

## Tests and gates

Repository-wide direct test run: **802 collected / 801 passed / 1 skipped / 0 failed**.
The skip requires `VISUAL_ENGINE_POSTGRES_DSN`.

A4 PASS; A5 PASS; A6 PASS; A7 OFFLINE PASS; A8 PASS; A9 PASS; A10 PASS.
V1.30 legacy-consumer audit PASS.

## Files created

- `tests/unit/test_v130_legacy_consumer_migration.py`
- `tools/verify_v130_legacy_consumer_migration.py`
- `tools/visual_qa_v130_legacy_consumer_migration.py`
- `docs/domains/color/V1.30_TYPED_BASE_CONSUMER_MIGRATION_CONTRACT.md`
- `docs/domains/color/V1.30_IMPLEMENTATION_REPORT_2026-09-23__part_01.md` (split document; see adjacent parts)
- `artifacts/v130_legacy_consumer_migration/V1.30_TYPED_VS_LEGACY_MIGRATION.png`
- `artifacts/v130_legacy_consumer_migration/V1.30_TYPED_BASE_CONSUMER_MIGRATION_EVIDENCE.json`
- `artifacts/v130_legacy_consumer_migration/V1.30_TYPED_BASE_CONSUMER_MIGRATION_MANIFEST.json`
- `artifacts/v130_legacy_consumer_migration/V1.30_RELEASE_EVIDENCE.txt`
