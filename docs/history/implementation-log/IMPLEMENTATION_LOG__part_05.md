<!-- Refactored from ['docs/history/implementation-log/IMPLEMENTATION_LOG__part_01.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_02.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_03.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_04.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_05.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_06.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_07.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_08.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_09.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_10.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_11.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_12.md']; source lines 558-697; content preserved. -->
<!-- Part 5/12. Use the family index for navigation. -->
## Files modified

- `src/visual_engine/runtime/typed_appearance_input.py`
- `src/visual_engine/runtime/base_resolution.py`
- `src/visual_engine/runtime/__init__.py`
- `src/visual_engine/runtime/version_policy.py`
- `pyproject.toml`
- `tools/verify_a4_docs.py`
- `tools/verify_a10_full_audit.py`
- `docs/governance/status/CURRENT_STATUS__part_01.md`
- `docs/governance/roadmap/ROADMAP__part_01.md`
- `docs/governance/architecture/ENGINE_VISION__part_01.md`
- `docs/governance/decisions/DECISIONS__part_01.md`
- `docs/history/implementation-log/IMPLEMENTATION_LOG__part_01.md` (split document; see adjacent parts)
- `artifacts/current_test_matrix/REPORT.json`

## Removed from current checkpoint

- `artifacts/v129_typed_appearance_input/`
- `artifacts/v128_appearance_role_bridge/`

Historical V1.28/V1.29 reports remain as provenance; superseded working boards do
not remain in the current checkpoint.

## Exact line snapshot

The exact final counts are recorded in the V1.30 release evidence after source and
documentation freeze. The principal changed implementation blocks are the direct
typed BASE hand-off in `typed_appearance_input.py`, the typed factories in
`base_resolution.py`, the public exports in `runtime/__init__.py`, and the version
policy. The new V1.30 test, verifier and visual QA files are entirely new.

## Explicit nonclaims

- LIVE_POSTGRES = UNVERIFIED
- PACKAGE_BUILD = NOT VERIFIED in this environment
- PRODUCTION_ART_QUALITY = NOT CLAIMED
- no COLOR algorithm was implemented
- no lighting/shading/BRDF/material-physics/render post-processing was implemented
- the legacy appearance input has not been removed or deprecated

## Next V1.31 micro-scope

Define and implement the first genuine typed COLOR-domain consumer only after a
closed COLOR contract exists. The next brick must specify the COLOR vocabulary,
value spaces, provenance, dependency/invalidation rules, fail-closed rejection of
BASE/MATERIAL/LIGHTING leakage, deterministic resolver behavior, generic
object/hand/plant coverage, Palette coverage, and a visual source → typed COLOR →
domain-resolution artifact. No renderer or lighting system should be pulled into
that work merely to make the output look richer.


# V1.31 — Typed COLOR Consumer Migration — 2026-09-23

## Objective

V1.31 implements the first genuinely typed COLOR-domain consumer without collapsing COLOR into
BASE or importing lighting/material semantics prematurely. The consumer must operate on the selected
semantic role, preserve canonical color and provenance, and remain independent from geometry and other
appearance domains.

## Implementation

1. Audited the existing COLOR contract and confirmed that its historical fields are broad compatibility
   vocabulary, not a typed COLOR algorithm.
2. Extended the closed domain validator with a typed `canonical_color` value kind and explicit typed
   COLOR output fields while retaining the historical compatibility vocabulary.
3. Relaxed the generic role hand-off boundary so a validated `AppearanceRoleContribution` may be an
   authority for BASE or COLOR, while still rejecting a second contribution in the same domain.
4. Added `TypedColorInput`, a deliberately minimal projection containing only target ID + role
   contribution + fingerprint.
5. Added `build_color_resolution_input_from_typed()` and `resolve_color_domain_from_typed()`.
6. Implemented the COLOR resolver as an identity-preserving authoritative consumer: it returns the
   canonical `ColorRGBA` object unchanged and emits role/source/authored provenance fields.
7. Added targeted COLOR invalidation by delegating authority selection to the existing role-bridge
   invalidation rules.
8. Added adversarial tests for duplicate authority, missing typed role, material/light leakage,
   tampering, dependency contradiction, alpha preservation, geometry/sibling independence and
   deterministic results.
9. Added a visual board from actual runtime outputs for authored, inherited, Palette and generated
   cases and manually inspected it.
10. Bumped engine/package version 1.3.6 → 1.3.7 and resolution identity 16 → 17.

## Self-critique / corrections

The first full-suite run correctly exposed a documentation-gate failure because the new V1.31 contract
had not yet been created; no code failure was hidden behind that test. A separate test draft initially
mutated a component hierarchy while retaining an already-materialized `RuntimeGraph`, which the graph
contract correctly rejects as stale. The tests were corrected to rebuild the graph after topology changes.
No production code was weakened to accommodate the test.

The visual board was also inspected rather than treated as a mathematical checksum. The alpha-bearing
sample is visibly presented on a checkerboard, while the runtime retains unassociated alpha. The other
three swatches correspond directly to the resolver's canonical output values.

## Visual QA

Generated and manually inspected:

`artifacts/v131_typed_color_consumer/V1.31_TYPED_COLOR_DOMAIN_RUNTIME.png`

The board is diagnostic evidence, not production artwork. It uses actual COLOR resolver output and
explicitly states the non-goals so the artifact cannot be mistaken for a lighting/shading result.

## Files created

- `src/visual_engine/runtime/color_resolution.py`
- `tests/unit/test_v131_color_resolution.py`
- `tools/verify_v131_typed_color_consumer.py`
- `tools/visual_qa_v131_typed_color_consumer.py`
- `docs/domains/color/V1.31_TYPED_COLOR_CONSUMER_CONTRACT__part_01.md` (split document; see adjacent parts)
- `docs/domains/color/V1.31_IMPLEMENTATION_REPORT_2026-09-23__part_01.md` (split document; see adjacent parts)
- `artifacts/v131_typed_color_consumer/V1.31_TYPED_COLOR_DOMAIN_RUNTIME.png`
- `artifacts/v131_typed_color_consumer/V1.31_TYPED_COLOR_CONSUMER_EVIDENCE.json`
- `artifacts/v131_typed_color_consumer/V1.31_TYPED_COLOR_CONSUMER_MANIFEST.json`
- `artifacts/v131_typed_color_consumer/V1.31_RELEASE_EVIDENCE.txt`

## Files modified

- `src/visual_engine/runtime/appearance_contract.py`
- `src/visual_engine/runtime/domain_resolution.py`
- `src/visual_engine/runtime/typed_appearance_input.py`
- `src/visual_engine/runtime/__init__.py`
- `src/visual_engine/runtime/version_policy.py`
- `pyproject.toml`
- `tools/verify_a4_docs.py`
- `tools/verify_a10_full_audit.py`
- `docs/governance/status/CURRENT_STATUS__part_01.md`
- `docs/governance/roadmap/ROADMAP__part_01.md`
- `docs/governance/architecture/ENGINE_VISION__part_01.md`
- `docs/governance/decisions/DECISIONS__part_01.md`
- `docs/history/implementation-log/IMPLEMENTATION_LOG__part_01.md` (split document; see adjacent parts)
- `artifacts/current_test_matrix/REPORT.json`

## Exact line snapshot

Final source/document line counts and exact changed ranges are recorded in the V1.31 implementation
report after the source freeze. This avoids claiming line numbers before all documentation/evidence
files are finalized.
