<!-- Refactored from ['docs/history/implementation-log/IMPLEMENTATION_LOG__part_01.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_02.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_03.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_04.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_05.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_06.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_07.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_08.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_09.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_10.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_11.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_12.md']; source lines 1-145; content preserved. -->
<!-- Part 1/12. Use the family index for navigation. -->
# V1.27 — Effective Appearance Composition Foundations — 2026-09-22

## Objective

Build the first renderer-neutral composition boundary between the typed BASE authority (V1.25)
and the typed Palette authority (V1.26), without introducing color mixing, lighting, shading or
material response. The composition layer answers only which already-resolved authority owns the
requested semantic role.

## Checkpoint provenance

The active filesystem contained the V1.25 certified archive but not a mountable V1.26 source ZIP.
Rather than claiming an unavailable V1.26 implementation was present, the V1.26 palette contract was
reconstructed from the preserved V1.26 implementation report and implemented in-place before V1.27.
This provenance gap is explicit in this log. The resulting checkpoint contains the typed Palette
implementation, its resolver/tests, and the V1.27 composition layer.

## What was implemented

1. Typed `Palette` authority with `primary`, `secondary`, `accent`, `detail` slots.
2. Authored/inherited/generated palette source identity and complete provenance.
3. Canonical linear-sRGB entries with exact authored sRGB preservation.
4. Whole-palette inheritance and explicit override policies.
5. Deterministic slot selection after authority resolution; no cross-authority slot mixing.
6. Targeted palette fingerprints/invalidation independent of geometry and transforms.
7. Persistence serialization and fingerprint tamper rejection for Palette.
8. `AppearanceCompositionRequest` and typed `AppearanceComposition`.
9. Explicit composition modes: BASE_ONLY, PALETTE_ONLY, BASE_THEN_PALETTE, PALETTE_THEN_BASE, REJECT_SAME_ROLE.
10. BASE/Palette provenance retained in composition output; no hidden third authority.
11. Explicit role-to-slot mapping for primary/secondary/accent/detail; background/custom fail closed.
12. Composition fingerprint limited to composition inputs and BASE/Palette resolution identities.
13. Adversarial tests for missing slots, authority conflicts, blocking inheritance, persistence tampering,
    contradictory requests and geometry independence.
14. Generic object + non-ocular `hand` samples using exactly the same contract.
15. Human-inspected source→resolved visual board generated before checkpoint promotion.

## Self-critique and corrections

- The invalidation design was checked against the subtle case where a local palette exists but a nearest
  ancestor has a conflict-capable policy. The dependency identity includes that ancestor when its policy
  can change the resolution outcome.
- No semantic fallback was permitted from `background`/`custom` to `primary`; that would create a visually
  plausible but semantically false positive.
- The composition result does not expose a synthetic blended color. The selected canonical value is exactly
  the value already owned by BASE or Palette.
- The visual board includes source sRGB swatches, resolved display swatches and simple geometry proxies. It
  was inspected and showed matching source/resolved display colors for resolved cases and an explicit
  `NO FALLBACK` state for the missing-slot case.

## Files created

- `src/visual_engine/components/common/palette.py`
- `src/visual_engine/runtime/palette_resolution.py`
- `src/visual_engine/runtime/appearance_composition.py`
- `tests/unit/test_v126_palette.py`
- `tests/unit/test_v127_appearance_composition.py`
- `tests/unit/test_v127_appearance_composition_persistence.py`
- `tools/visual_qa_v127_appearance_composition.py`
- `tools/verify_v127_appearance_composition.py`
- `docs/domains/color/V1.26_PALETTE_MODEL_CONTRACT.md`
- `docs/domains/color/V1.27_EFFECTIVE_APPEARANCE_COMPOSITION_CONTRACT.md`
- `artifacts/history/v1.27/appearance_composition/V1.27_APPEARANCE_COMPOSITION_SOURCE_TO_RESOLUTION.png`

## Files modified

- `src/visual_engine/components/common/meta.py` — typed `Component.palette` authority.
- `src/visual_engine/components/common/__init__.py` — Palette exports.
- `src/visual_engine/model/__init__.py` — Palette compatibility exports.
- `src/visual_engine/runtime/__init__.py` — Palette/composition exports.
- `src/visual_engine/runtime/version_policy.py` — resolution version advanced from 12 to 13 because
  composition semantics change cache identity.
- `src/visual_engine/persistence/serialization.py` — Palette serialization, rehydration and fingerprint verification.
- `docs/governance/status/CURRENT_STATUS__part_01.md` — current frontier advanced to V1.27.
- `docs/governance/roadmap/ROADMAP__part_01.md` — V1.26/V1.27 state and execution order.
- `docs/governance/architecture/ENGINE_VISION__part_01.md` — current structural priority.
- `docs/governance/decisions/DECISIONS__part_01.md` — D-073 composition authority decision.
- `tools/verify_a4_docs.py` — current frontier assertions.
- `tools/verify_a10_full_audit.py` — current checkpoint assertions.
- `tests/unit/test_v13_domain_resolution.py` — historical resolution expectation synchronized to policy.

## Exact line snapshot

The final line counts, artifact hashes and source/test fingerprint are generated in the release evidence
after the final complete test run and cache cleanup.

## Current status

`V1.27 ENGINEERING PASS / EFFECTIVE APPEARANCE SELECTION READY / NO LIGHTING OR SHADING CLAIM`

## Next step — V1.28 Renderer-neutral Appearance Role Bridge

1. Define a typed role contribution envelope that can carry BASE and Palette-selected canonical colors
   without reverting to free-form dictionaries.
2. Decide exactly how the legacy `AppearanceResolutionInput.base_color` hex field is bridged or deprecated
   without breaking historical callers.
3. Add a compatibility adapter with explicit source/provenance rather than silently replacing the old field.
4. Define role-level invalidation separately from geometry and from future lighting/material caches.
5. Add persistence tests for composition/role envelopes and stale provenance.
6. Add generic object, hand and one non-ocular component-family samples.
7. Produce a visual role bridge board before renderer integration.

Explicitly defer shadows, highlights, lighting, BRDF, metallic/roughness response, transmission,
reflection, style response, gamut mapping and renderer-specific post-processing.

## Artifact retention cleanup — historical A5 source retention

Historical A5 visual QA remains reproducible from its source scripts and verifier. The checkpoint
retains source-level evidence rather than treating stale generated images as authoritative output.
The current checkpoint retains only `artifacts/v17_canthus_terminal_transform/` for the historical
A5 visual surface; newer V1.24+ artifacts are stored under their own versioned artifact directories.

## Final exact line/change snapshot — V1.27

Created files:
- `src/visual_engine/components/common/palette.py`: 276 lines
- `src/visual_engine/runtime/palette_resolution.py`: 153 lines
- `src/visual_engine/runtime/appearance_composition.py`: 202 lines
- `tests/unit/test_v126_palette.py`: 124 lines
- `tests/unit/test_v127_appearance_composition.py`: 131 lines
- `tests/unit/test_v127_appearance_composition_persistence.py`: 28 lines
- `tools/visual_qa_v127_appearance_composition.py`: 113 lines
- `tools/verify_v127_appearance_composition.py`: 34 lines
- `docs/domains/color/V1.26_PALETTE_MODEL_CONTRACT.md`: 21 lines
- `docs/domains/color/V1.27_EFFECTIVE_APPEARANCE_COMPOSITION_CONTRACT.md`: 107 lines

Modified files / affected regions:
- `src/visual_engine/components/common/meta.py`: imports 9–10; typed palette field/validation 110–125.
- `src/visual_engine/components/common/__init__.py`: Palette exports 11–15.
- `src/visual_engine/model/__init__.py`: Palette compatibility exports (tail block).
- `src/visual_engine/runtime/__init__.py`: Palette resolver exports 182–189; composition exports 190–201.
- `src/visual_engine/runtime/version_policy.py`: current V1.x wording line 1; `RESOLUTION_VERSION=13` line 22.
- `src/visual_engine/persistence/serialization.py`: Palette serialization 150–191; rehydration 193–235; component payload 250; component reconstruction 337.
- `tools/verify_a4_docs.py`: current V1.27 checkpoint/contract markers and order assertions.
- `tools/verify_a10_full_audit.py`: current V1.27 checkpoint/order/contract markers and D-073 marker.
- `tests/unit/test_v13_domain_resolution.py`: historical resolution assertion synchronized to canonical `RESOLUTION_VERSION`.
- `docs/governance/status/CURRENT_STATUS__part_01.md`, `docs/governance/roadmap/ROADMAP__part_01.md`, `docs/governance/architecture/ENGINE_VISION__part_01.md`, `docs/governance/decisions/DECISIONS__part_01.md`, `docs/history/implementation-log/IMPLEMENTATION_LOG__part_01.md` (split document; see adjacent parts): V1.27 frontier/history synchronization.

Final source/test fingerprint: `3f098696796f256a67ca77c9c9ee49d23e0ade001cf56b6b5b85f7f84dad0fe7` over 258 Python source/test files.
Repository test evidence: 759 collected / 758 passed / 1 skipped / 0 failed.

## Final gate closure

A4 PASS · A5 PASS · A6 PASS · A7 OFFLINE PASS · A8 PASS · A9 PASS · A10 PASS.
LIVE_POSTGRES=UNVERIFIED · PACKAGE_BUILD=NOT_VERIFIED · PRODUCTION_ART_QUALITY=NOT_CLAIMED.
