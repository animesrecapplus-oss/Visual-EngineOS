<!-- Refactored from ['docs/history/implementation-log/IMPLEMENTATION_LOG__part_01.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_02.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_03.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_04.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_05.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_06.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_07.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_08.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_09.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_10.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_11.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_12.md']; source lines 279-419; content preserved. -->
<!-- Part 3/12. Use the family index for navigation. -->
## Files modified

- `src/visual_engine/runtime/appearance_composition.py`
- `src/visual_engine/runtime/appearance_contract.py`
- `src/visual_engine/runtime/version_policy.py`
- `src/visual_engine/runtime/__init__.py`
- `docs/governance/status/CURRENT_STATUS__part_01.md`
- `docs/governance/roadmap/ROADMAP__part_01.md`
- `docs/governance/architecture/ENGINE_VISION__part_01.md`
- `docs/governance/decisions/DECISIONS__part_01.md`
- `docs/history/implementation-log/IMPLEMENTATION_LOG__part_01.md` (split document; see adjacent parts)
- `tools/verify_a4_docs.py`
- `tools/verify_a10_full_audit.py`
- `artifacts/current_test_matrix/REPORT.json`

## Exact line snapshot after implementation

- `src/visual_engine/runtime/appearance_role_bridge.py`: 230 lines
- `src/visual_engine/runtime/appearance_composition.py`: 210 lines
- `src/visual_engine/runtime/appearance_contract.py`: 391 lines
- `src/visual_engine/runtime/version_policy.py`: 34 lines
- `tests/unit/test_v128_appearance_role_bridge.py`: 223 lines
- `tools/visual_qa_v128_appearance_role_bridge.py`: 103 lines
- `tools/verify_v128_appearance_role_bridge.py`: 57 lines
- `docs/domains/color/V1.28_APPEARANCE_ROLE_BRIDGE_CONTRACT.md`: 72 lines
- `docs/governance/status/CURRENT_STATUS__part_01.md`: 96 lines
- `docs/governance/roadmap/ROADMAP__part_01.md`: 1528 lines
- `docs/governance/architecture/ENGINE_VISION__part_01.md`: 1053 lines
- `docs/governance/decisions/DECISIONS__part_01.md`: 1075 lines
- `docs/history/implementation-log/IMPLEMENTATION_LOG__part_01.md` (split document; see adjacent parts): 1204 lines before this entry was appended; final line count is recorded by the release report.
- `tools/verify_a4_docs.py`: 90 lines
- `tools/verify_a10_full_audit.py`: 272 lines

## Explicit nonclaims

- LIVE_POSTGRES = UNVERIFIED
- PACKAGE_BUILD = NOT VERIFIED in the current environment
- PRODUCTION_ART_QUALITY = NOT CLAIMED
- No lighting/shading/material/BRDF/transmission/reflection/style response was added.

## Next step — V1.29 Typed Appearance Input Promotion

The bridge is now proven, but the old `AppearanceResolutionInput.base_color` field is
still structurally present. V1.29 should promote the typed role contribution into the
canonical renderer-neutral input while retaining a narrowly-scoped legacy adapter.

Micro-features:

1. define the canonical typed appearance input envelope;
2. make `AppearanceRoleContribution` the authoritative BASE/COLOR entry point;
3. mark the legacy hexadecimal `base_color` as compatibility-derived data;
4. make the BASE domain resolver consume the typed contribution without duplicate
   authority;
5. reject typed-vs-legacy divergence before domain resolution;
6. propagate role provenance into `DomainResolutionProvenance`;
7. include role-bridge dependency identity in domain resolution fingerprints;
8. keep geometry, transforms and unrelated siblings out of appearance invalidation;
9. add persistence/tampering tests for the typed envelope;
10. validate generic object, hand and another non-ocular component;
11. generate source → typed-input → domain-resolution visual evidence;
12. only after those checks, evaluate whether the legacy field can be deprecated.

Still explicitly outside V1.29: shadows, highlights, lighting, BRDF, metallic/roughness,
transmission compositing, reflection, style response, gamut mapping and renderer-specific
post-processing.


# V1.29 — Typed Appearance Input Promotion — 2026-09-23

## Objective

Promote the V1.28 typed role contribution from a compatibility bridge into the canonical
renderer-neutral appearance input path, while preserving the old hexadecimal field only as
derived compatibility data. The critical acceptance condition is that the BASE domain resolver
can no longer accidentally read an independent legacy color when a typed role is present.

## Starting point

The implementation started from the certified V1.28 checkpoint and revalidated the working archive
SHA before modification. V1.28 already carried `AppearanceRoleContribution`, provenance-preserving
BASE/Palette composition, and legacy-boundary contradiction checks. V1.29 therefore extends that
contract instead of recreating color or palette logic.

## Implementation

1. Added `TypedAppearanceInput` as the canonical renderer-neutral envelope.
2. Added a typed-role slot to `DomainResolutionInput`; it is legal only for the BASE domain.
3. Added automatic `appearance_role_bridge` dependency identity using the exact role fingerprint.
4. Updated `resolve_base_domain()` so the typed role is authoritative; the old contribution path
   remains only for pre-V1.29 compatibility.
5. Extended `DomainResolutionProvenance` with role bridge fingerprint, authority component, source ID
   and lineage, with validation against the input.
6. Added a dedicated `build_base_resolution_input_from_role()` factory so callers cannot accidentally
   manufacture a legacy BASE contribution when using the canonical path.
7. Bumped `RESOLUTION_VERSION` 14 → 15 and `BASE_RESOLVER_VERSION` 1 → 2.
8. Added adversarial tests for authority duplication, tampered fingerprints, dependency contradiction,
   geometry independence, persistence round-trip and generic object/hand/plant use.

## Self-critique / corrections

The first implementation attempt exposed an important contract issue: a typed BASE result used a synthetic
role contribution identity but the generic provenance validator still expected only legacy contribution IDs.
This was corrected by making the validator explicitly recognize the canonical role identity
(`role:<role-fingerprint>`). No exception was hidden and no false-positive result was retained.

A second test assumption was corrected during persistence review: component serialization persists a component
authority, not its arbitrary child graph. The test now restores the persisted authority first and then attaches
a fresh generic target, which tests the actual persistence contract instead of inventing child round-trip semantics.

## Visual QA

Generated `artifacts/v129_typed_appearance_input/V1.29_TYPED_INPUT_SOURCE_TO_DOMAIN.png`. The board uses the
actual runtime outputs for three generic non-ocular targets: object, hand and plant. It shows the selected
canonical display value, derived legacy spelling, BASE-domain output, role fingerprint, typed-input fingerprint
and provenance/lineage alongside simple geometry proxies. The proxies are explicitly labelled as non-production
art; they are evidence that the semantic value reaches visible geometry consistently, not a claim of renderer quality.
The artifact was manually inspected after generation.

## Tests

Focused V1.29 suite: 15 tests passed. Combined relevant V1.28/V1.29/domain suites: 63 tests passed.
Repository-wide direct run: 792 collected / 791 passed / 1 skipped / 0 failed. The only skipped test requires
`VISUAL_ENGINE_POSTGRES_DSN`; live PostgreSQL remains unverified.

## Gates

A4–A10 are rerun after documentation and evidence regeneration. A8 must remain byte-stable across two verifier runs.

## Files created

- `src/visual_engine/runtime/typed_appearance_input.py`
- `tests/unit/test_v129_typed_appearance_input.py`
- `tools/visual_qa_v129_typed_appearance_input.py`
- `tools/verify_v129_typed_appearance_input.py`
- `docs/domains/color/V1.29_TYPED_APPEARANCE_INPUT_CONTRACT.md`
- `docs/domains/color/V1.29_IMPLEMENTATION_REPORT_2026-09-23__part_01.md` (split document; see adjacent parts)
- `artifacts/v129_typed_appearance_input/V1.29_TYPED_INPUT_SOURCE_TO_DOMAIN.png`
- `artifacts/v129_typed_appearance_input/V1.29_TYPED_APPEARANCE_INPUT_EVIDENCE.json`
- `artifacts/v129_typed_appearance_input/V1.29_TYPED_APPEARANCE_INPUT_MANIFEST.json`
- `artifacts/v129_typed_appearance_input/V1.29_RELEASE_EVIDENCE.txt`
